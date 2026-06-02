"""Gibberish detection guardrail implementation.

Includes a fast, regex-based prefilter that runs before the DSPy LLM call.
The prefilter scores surface features (keyboard mashes, repeated characters,
all-consonant runs, punctuation spam) and structural heuristics (vowel ratio,
no-whitespace long strings) to short-circuit obvious gibberish without an
LLM round-trip.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import GibberishGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)

# --------------------------------------------------------------------------- #
# Signal catalog                                                               #
# --------------------------------------------------------------------------- #

# Each entry: (slug, regex, score_weight). Weights are tuned for low
# false-positive rate on normal English text while catching obvious junk.
GIBBERISH_SIGNALS: List[Tuple[str, str, float]] = [
    ("all_consonants", r"[bcdfghjklmnpqrstvwxyz]{8,}", 0.7),
    ("qwerty_row", r"[qwertyuiop]{5,}", 0.25),
    ("asdf_row", r"[asdfghjkl]{5,}", 0.25),
    ("zxcv_row", r"[zxcvbnm]{5,}", 0.25),
    ("single_char_repeat", r"(.)\1{5,}", 0.4),
    ("punctuation_spam", r"[!?\.\,]{5,}", 0.3),
]

# Vowels used for ratio calculation.
_VOWELS = set("aeiou")

# Minimum text length for the "no whitespace" heuristic.
_DEFAULT_NO_WS_MIN_LENGTH = 30

# Minimum text length for the vowel-ratio structural check.
_VOWEL_RATIO_MIN_LENGTH = 30

# Threshold below which the vowel ratio triggers a structural score.
_VOWEL_RATIO_THRESHOLD = 0.10


# --------------------------------------------------------------------------- #
# ReDoS safety                                                                 #
# --------------------------------------------------------------------------- #


def _is_unsafe_pattern(pattern: str) -> bool:
    """Heuristic ReDoS screen. Returns True for patterns that exhibit the
    canonical catastrophic-backtracking shapes: nested quantifiers
    ``(X+)+``, ``(X*)*``, ``(X+)*``, ``(X*)+`` and overlapping-alternation
    quantifiers ``(X|Y)*``, ``(X|Y)+``.

    This is intentionally a static, conservative check - it rejects a
    small number of safe patterns in exchange for never accepting a
    known-bad one at config time. Matches the documented rule:
    "patterns with nested quantifiers like ``(a+)+`` or ``(a|a)*`` are
    rejected".
    """
    # (X+)+, (X*)+, (X+)*, (X*)*  (no other group nesting for the
    # static check to stay simple)
    if re.search(r"\([^()]*[+*][^()]*\)[+*]", pattern):
        return True
    # (X|Y)+, (X|Y)*  - any alternation inside a quantified group
    if re.search(r"\([^()]*\|[^()]*\)[+*]", pattern):
        return True
    return False


# --------------------------------------------------------------------------- #
# Structural helpers                                                           #
# --------------------------------------------------------------------------- #


def _vowel_ratio(text: str) -> float:
    """Count vowels / count letters (case-insensitive). Returns 0.0 when
    the text contains no alphabetic characters."""
    letters = [c for c in text.lower() if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c in _VOWELS) / len(letters)


def _has_no_whitespace(text: str, min_length: int = _DEFAULT_NO_WS_MIN_LENGTH) -> bool:
    """True when *text* has zero spaces and is at least *min_length* chars."""
    return " " not in text and len(text) >= min_length


# --------------------------------------------------------------------------- #
# Prefilter result type                                                        #
# --------------------------------------------------------------------------- #


@dataclass
class _GibberishSignal:
    """One regex prefilter hit."""

    slug: str
    matched_text: str
    score: float


# --------------------------------------------------------------------------- #
# Gibberish guardrail                                                          #
# --------------------------------------------------------------------------- #


class GuardrailsGibberishSignature(dspy.Signature):
    """You are a content quality analysis system.
    Your task is to determine if the input text is gibberish, nonsensical, or random characters.

    Gibberish includes:
    - Random strings of characters (e.g., "asdfghjkl")
    - Repetitive loops of words or characters
    - Text that lacks any semantic meaning
    - Word salad (words that don't form coherent sentences)
    - Mixed, unrelated character sets unless intentional

    Provide a probability score (0.0 to 1.0) of the text being gibberish."""

    user_input: str = dspy.InputField(desc="The text content to analyze.")
    gibberish_probability: float = dspy.OutputField(
        desc="A probability score between 0.0 and 1.0 that the text is gibberish."
    )
    is_gibberish: bool = dspy.OutputField(
        desc="True if the text is identified as gibberish/nonsense."
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation of why the text is or isn't gibberish."
    )


class GibberishGuardrail(BaseGuardrail):
    """Guardrail for detecting nonsensical or random text.

    Runs a fast, deterministic regex + heuristic prefilter before
    delegating to a DSPy ChainOfThought program for nuanced analysis.
    When the prefilter score exceeds ``prob_threshold``, the LLM call
    is skipped entirely.
    """

    def __init__(self, config: GibberishGuardrailConfig):
        """Initialize the gibberish guardrail.

        Args:
            config: Configuration for the gibberish guardrail
        """
        super().__init__(config)
        self.config: GibberishGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsGibberishSignature)

        # Compile signal patterns when the prefilter is enabled.
        self._compiled_signals: List[Tuple[str, re.Pattern[str], float]] = []
        if self.config.enable_regex_prefilter:
            for slug, pattern, weight in GIBBERISH_SIGNALS:
                self._compiled_signals.append((slug, re.compile(pattern), weight))

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "gibberish"

    def _configure_dspy(self) -> None:
        """Configure DSPy for gibberish guardrail."""
        configure_dspy_from_config(self.config)

    # ------------------------------------------------------------------ #
    # Prefilter                                                            #
    # ------------------------------------------------------------------ #

    def _find_signals(self, text: str) -> List[_GibberishSignal]:
        """Run all regex signals and evaluate structural heuristics.

        Returns a list of ``_GibberishSignal`` instances — one per
        matched regex pattern. Structural heuristics are scored
        separately in ``_score()``.
        """
        signals: List[_GibberishSignal] = []

        for slug, pat, weight in self._compiled_signals:
            for m in pat.finditer(text):
                signals.append(
                    _GibberishSignal(
                        slug=slug,
                        matched_text=m.group(0),
                        score=weight,
                    )
                )

        return signals

    def _score(self, signals: List[_GibberishSignal], text: str) -> float:
        """Sum signal scores plus structural heuristic bonuses, capped at 1.0."""
        total = sum(s.score for s in signals)

        # Structural: very low vowel ratio in long text.
        if (
            len(text) >= _VOWEL_RATIO_MIN_LENGTH
            and _vowel_ratio(text) < _VOWEL_RATIO_THRESHOLD
        ):
            total += 0.5

        # Structural: no whitespace in a long string.
        if _has_no_whitespace(text):
            total += 0.4

        return min(total, 1.0)

    def _run_regex_prefilter(
        self, input_text: str
    ) -> Tuple[float, List[_GibberishSignal]]:
        """Run the prefilter. Returns ``(score, signals)``.

        Short text (< 10 chars) returns ``(0.0, [])`` — too short to
        reliably judge.
        """
        if len(input_text) < 10:
            return 0.0, []

        signals = self._find_signals(input_text)
        score = self._score(signals, input_text)
        return score, signals

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text is gibberish.

        The regex prefilter runs first. When its score meets or exceeds
        ``prob_threshold`` the LLM is skipped and ``is_allowed=False``.
        Otherwise the request falls through to the DSPy LLM.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content is gibberish
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

        # 1. Fast regex + heuristic prefilter.
        if self.config.enable_regex_prefilter:
            score, signals = self._run_regex_prefilter(input_text)
            if score >= self.config.prob_threshold:
                return GuardrailResult(
                    is_allowed=False,
                    reason=f"Gibberish detected (score: {score:.2f})",
                    metadata={
                        "method": "regex_prefilter",
                        "gibberish_probability": score,
                        "is_gibberish": True,
                        "signals": [
                            {
                                "slug": s.slug,
                                "matched_text": s.matched_text,
                                "score": s.score,
                            }
                            for s in signals
                        ],
                    },
                    guardrail_name=self.name,
                )

        # 2. LLM-based analysis via DSPy.
        try:
            result = self._program(user_input=input_text)

            is_flagged = (
                result.is_gibberish
                or result.gibberish_probability >= self.config.prob_threshold
            )
            is_allowed = not is_flagged

            reason = None
            if is_flagged:
                reason = (
                    result.reason
                    or f"Nonsensical content detected (score: {result.gibberish_probability:.2f})"
                )

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "gibberish_probability": result.gibberish_probability,
                    "is_gibberish": result.is_gibberish,
                    "explanation": result.reason,
                    "threshold": self.config.prob_threshold,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during gibberish check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
