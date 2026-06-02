"""Toxicity detection guardrail implementation.

Includes a fast, regex-based prefilter that runs before the DSPy LLM
call.  The prefilter is intentionally conservative — low recall, very
high precision — and only catches unambiguous, severe cases (explicit
threats, self-harm encouragement, severe slurs with common obfuscation,
sexual violence indicators, encouragement of illegal drugs, and doxxing
indicators).  Mild profanity and contextual toxicity remain the LLM's
responsibility.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import ToxicityGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)

# --------------------------------------------------------------------------- #
# Conservative severe-toxicity pattern catalog                                 #
# --------------------------------------------------------------------------- #
# Each pattern is intentionally narrow.  False positives here are very
# expensive (silencing legitimate users), so the catalog is small and
# restricted to unambiguous, severe cases.

SEVERE_TOXICITY_PATTERNS: Dict[str, str] = {
    # Explicit threats of violence
    "explicit_threat": r"\b(i|we|they|he|she|you)\s+will\s+(kill|murder|hurt|harm|end)\s+you\b",
    # Self-harm encouragement
    "kill_yourself": r"\b(kys|kill\s*your\s*self|go\s+die|drop\s+dead)\b",
    # Racial slurs with common obfuscation (lowercase variants)
    "n_word_obfuscated": r"\bn[i!1\*][gq]{2}[aaeu]r\b",
    "k_word_obfuscated": r"\bk[i!1\*]{2}e\b",
    "f_slur_obfuscated": r"\bf[a@\*][gq]{2}[o0]t\b",
    "c_slur_obfuscated": r"\bc\s*[h\*]\s*[i!1\*]\s*n\s*k\b",
    "s_slur_obfuscated": r"\bs\s*p\s*[i!1\*]\s*c\b",
    # Sexual violence
    "sexual_violence": r"\b(rape|raped|raping|molest|molested|molesting)\s+(you|her|him|them|a\s+(child|minor|kid))\b",
    # Encouragement of illegal drugs
    "encourage_drugs": r"\b(do|shoot|snort|smoke|try|use)\s+(heroin|meth|cocaine|crack|fentanyl)\b",
    # Doxxing indicators
    "doxxing": r"\b(here\s+is|i\s+have|i\s+know)\s+your\s+(address|home\s+address|ssn|social\s+security\s+number|phone\s+number)\b",
}


# --------------------------------------------------------------------------- #
# Prefilter result types                                                       #
# --------------------------------------------------------------------------- #


@dataclass
class _ToxicityMatch:
    """One regex prefilter hit."""

    slug: str
    matched_text: str


# --------------------------------------------------------------------------- #
# Toxicity guardrail                                                           #
# --------------------------------------------------------------------------- #


class GuardrailsToxicitySignature(dspy.Signature):
    """You are a toxicity detection system.
    Your task is to analyze text and determine if it contains toxic, insulting, or harmful language.

    Toxicity includes:
    - Insults and derogatory language
    - Personal attacks
    - Threatening language
    - Hate speech (not already covered by NSFW)
    - Harassment
    - Severe profanity

    Provide a toxicity score between 0.0 and 1.0."""

    user_input: str = dspy.InputField(desc="The text content to analyze for toxicity.")
    toxicity_types: Optional[List[str]] = dspy.OutputField(
        desc="List of detected toxicity types (e.g., 'insult', 'threat', 'hate_speech')."
    )
    toxicity_score: float = dspy.OutputField(
        desc="A score between 0.0 and 1.0 indicating the level of toxicity."
    )
    is_toxic: bool = dspy.OutputField(
        desc="Boolean indicating if the content exceeds acceptable toxicity levels."
    )
    reason: str = dspy.OutputField(desc="Brief explanation of the toxicity assessment.")


class ToxicityGuardrail(BaseGuardrail):
    """Guardrail for detecting toxic and harmful language.

    Runs a fast, deterministic regex prefilter (conservative severe-
    toxicity catalog) before delegating to a DSPy ChainOfThought
    program for nuanced analysis.  On a prefilter match the LLM call
    is skipped entirely and ``is_allowed=False`` is returned.
    """

    def __init__(self, config: ToxicityGuardrailConfig):
        """Initialize the toxicity guardrail.

        Args:
            config: Configuration for the toxicity guardrail
        """
        super().__init__(config)
        self.config: ToxicityGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsToxicitySignature)

        # Compile the severe-toxicity catalog when the prefilter is enabled.
        self._compiled_patterns: Dict[str, re.Pattern[str]] = {}
        if self.config.enable_regex_prefilter:
            for slug, pat in SEVERE_TOXICITY_PATTERNS.items():
                self._compiled_patterns[slug] = re.compile(pat)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "toxicity"

    def _configure_dspy(self) -> None:
        """Configure DSPy for toxicity guardrail."""
        configure_dspy_from_config(self.config)

    # ------------------------------------------------------------------ #
    # Prefilter                                                            #
    # ------------------------------------------------------------------ #

    def _find_matches(self, text: str) -> List[_ToxicityMatch]:
        """Run all compiled patterns and return a list of matches."""
        matches: List[_ToxicityMatch] = []
        for slug, pat in self._compiled_patterns.items():
            for m in pat.finditer(text):
                matches.append(_ToxicityMatch(slug=slug, matched_text=m.group(0)))
        return matches

    def _run_regex_prefilter(self, input_text: str) -> List[_ToxicityMatch]:
        """Run the prefilter.  Returns matches (empty list means no hit)."""
        return self._find_matches(input_text)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains toxic content.

        The regex prefilter runs first.  On any match the LLM is
        skipped and ``is_allowed=False`` with ``method="regex_prefilter"``.
        When no match is found the request falls through to the DSPy
        ChainOfThought program.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content is toxic
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

        # 1. Fast regex prefilter.  On any match, skip the LLM.
        if self._compiled_patterns:
            matches = self._run_regex_prefilter(input_text)
            if matches:
                slugs = sorted({m.slug for m in matches})
                matched_patterns = [
                    {"slug": m.slug, "matched_text": m.matched_text} for m in matches
                ]
                return GuardrailResult(
                    is_allowed=False,
                    reason=f"Severe toxicity detected: {slugs[0]}",
                    metadata={
                        "method": "regex_prefilter",
                        "is_toxic": True,
                        "toxicity_score": 1.0,
                        "toxicity_types": slugs,
                        "matched_patterns": matched_patterns,
                        "threshold": self.config.toxicity_threshold,
                    },
                    guardrail_name=self.name,
                )

        # 2. LLM-based analysis via DSPy.
        try:
            result = self._program(user_input=input_text)

            # Use threshold-based check as well as the boolean flag from LLM
            is_flagged = (
                result.is_toxic
                or result.toxicity_score >= self.config.toxicity_threshold
            )
            is_allowed = not is_flagged

            reason = None
            if is_flagged:
                reason = (
                    result.reason
                    or f"Toxicity detected (score: {result.toxicity_score:.2f})"
                )

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "toxicity_score": result.toxicity_score,
                    "toxicity_types": result.toxicity_types or [],
                    "is_toxic": result.is_toxic,
                    "explanation": result.reason,
                    "threshold": self.config.toxicity_threshold,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during toxicity check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
