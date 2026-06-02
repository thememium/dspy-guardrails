"""Keyword filtering guardrail implementation.

Includes a fast, regex-based prefilter that runs before the DSPy LLM
call.  Keywords are compiled into ``re.Pattern`` objects at construction
time with optional word-boundary anchoring, wildcard expansion
(``*`` → ``.*``, ``?`` → ``.``), and case-insensitive matching.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import KeywordsGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)

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
    known-bad one at config time.
    """
    # (X+)+, (X*)+, (X+)*, (X*)*
    if re.search(r"\([^()]*[+*][^()]*\)[+*]", pattern):
        return True
    # (X|Y)+, (X|Y)*  - any alternation inside a quantified group
    if re.search(r"\([^()]*\|[^()]*\)[+*]", pattern):
        return True
    return False


# --------------------------------------------------------------------------- #
# Keyword compilation                                                         #
# --------------------------------------------------------------------------- #


def _compile_keyword(
    keyword: str,
    *,
    word_boundary: bool,
    use_wildcards: bool,
    case_sensitive: bool,
) -> re.Pattern[str]:
    """Compile a single keyword into a ``re.Pattern``.

    Processing order matters:

    1. ``re.escape`` the literal keyword.
    2. If ``use_wildcards`` is True, translate the escaped wildcard
       characters (``\\*`` → ``.*``, ``\\?`` → ``.``).
    3. Optionally wrap in ``\\b…\\b`` when ``word_boundary`` is True
       **and** wildcards are disabled (since ``*``/``?`` expand to
       non-word characters that break ``\\b`` semantics).
    4. Apply ``re.IGNORECASE`` when ``case_sensitive`` is False.
    """
    escaped = re.escape(keyword)

    if use_wildcards:
        escaped = escaped.replace(r"\*", ".*").replace(r"\?", ".")

    if word_boundary and not use_wildcards:
        escaped = rf"\b{escaped}\b"

    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(escaped, flags)


# --------------------------------------------------------------------------- #
# Prefilter result type                                                        #
# --------------------------------------------------------------------------- #


@dataclass
class _KeywordMatch:
    """One regex prefilter hit."""

    keyword: str
    matched_text: str


# --------------------------------------------------------------------------- #
# Keywords guardrail                                                           #
# --------------------------------------------------------------------------- #


class GuardrailsKeywordsSignature(dspy.Signature):
    """You are a content filter that detects blocked keywords and phrases in text.

    Your task is to analyze text and determine if it contains any blocked keywords or phrases.
    You should be case-insensitive unless specified otherwise, and consider variations and misspellings.

    Blocked keywords are terms that should not appear in the content. Common examples include:
    - Profanity and offensive language
    - Hate speech terms
    - Sensitive or restricted terminology
    - Brand names that shouldn't be mentioned
    - Any custom terms specified as blocked

    Consider the context - sometimes words might appear in innocent contexts, but if they match
    blocked keywords, they should still be flagged."""

    blocked_keywords: List[str] = dspy.InputField(
        desc="List of keywords and phrases that are blocked."
    )
    user_input: str = dspy.InputField(
        desc="The text content to analyze for blocked keywords."
    )
    case_sensitive: bool = dspy.InputField(
        desc="Whether the keyword matching should be case sensitive."
    )
    reason: str = dspy.OutputField(
        desc="Explanation of why the content was flagged or why it passed the filter."
    )
    matched_keywords: Optional[List[str]] = dspy.OutputField(
        desc="List of blocked keywords that were found in the text. Empty if no matches."
    )
    contains_blocked: bool = dspy.OutputField(
        desc="Boolean indicating if the text contains any blocked keywords. True if blocked content found, False if clean."
    )


class KeywordsGuardrail(BaseGuardrail):
    """Guardrail for filtering content based on blocked keywords.

    Runs a fast, deterministic regex prefilter (compiled keywords with
    optional word-boundary anchoring and wildcard expansion) before
    delegating to a DSPy ChainOfThought program for nuanced analysis.
    When the prefilter finds a match it short-circuits with
    ``is_allowed=False`` and ``method="regex_prefilter"``, skipping the
    LLM call entirely.
    """

    def __init__(self, config: KeywordsGuardrailConfig):
        """Initialize the keywords guardrail.

        Args:
            config: Configuration for the keywords guardrail
        """
        super().__init__(config)
        self.config: KeywordsGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsKeywordsSignature)

        # Compile keywords for the regex prefilter.
        self._compiled_keywords: List[Tuple[str, re.Pattern[str]]] = []
        if self.config.enable_regex_prefilter:
            for kw in self.config.blocked_keywords or []:
                if self.config.use_wildcards and _is_unsafe_pattern(kw):
                    raise ValueError(
                        f"blocked keyword {kw!r} contains patterns that "
                        f"could cause catastrophic backtracking (ReDoS)"
                    )
                pattern = _compile_keyword(
                    kw,
                    word_boundary=self.config.word_boundary,
                    use_wildcards=self.config.use_wildcards,
                    case_sensitive=self.config.case_sensitive,
                )
                self._compiled_keywords.append((kw, pattern))

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "keywords"

    def _configure_dspy(self) -> None:
        """Configure DSPy for keywords guardrail."""
        configure_dspy_from_config(self.config)

    # ------------------------------------------------------------------ #
    # Prefilter                                                            #
    # ------------------------------------------------------------------ #

    def _find_matches(self, text: str) -> List[_KeywordMatch]:
        """Run all compiled keywords and return a list of matches."""
        matches: List[_KeywordMatch] = []
        for kw, pat in self._compiled_keywords:
            for m in pat.finditer(text):
                matches.append(_KeywordMatch(keyword=kw, matched_text=m.group(0)))
        return matches

    def _run_regex_prefilter(self, input_text: str) -> List[_KeywordMatch]:
        """Run the prefilter. Returns matches (empty list if none)."""
        if not self.config.enable_regex_prefilter:
            return []
        return self._find_matches(input_text)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains blocked keywords.

        The regex prefilter runs first.  On a match the LLM is skipped
        and ``is_allowed=False``.  Only when no regex match is found do
        we fall through to the DSPy LLM (or the simple substring
        fallback if DSPy is not configured / fails).

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content contains blocked keywords
        """

        # Simple string matching fallback for basic functionality
        def simple_keyword_check(
            text: str, keywords: List[str], case_sensitive: bool = False
        ) -> tuple[bool, List[str]]:
            """Simple string matching for blocked keywords."""
            found_keywords = []
            search_text = text if case_sensitive else text.lower()

            for keyword in keywords:
                search_keyword = keyword if case_sensitive else keyword.lower()
                if search_keyword in search_text:
                    found_keywords.append(keyword)

            return len(found_keywords) > 0, found_keywords

        # 1. Fast regex prefilter.  On any match, skip the LLM.
        matches = self._run_regex_prefilter(input_text)
        if matches:
            matched_kws = sorted({m.keyword for m in matches})
            return GuardrailResult(
                is_allowed=False,
                reason=f"Blocked keywords detected: {', '.join(matched_kws)}",
                metadata={
                    "method": "regex_prefilter",
                    "contains_blocked": True,
                    "matched_keywords": matched_kws,
                    "blocked_keywords": self.config.blocked_keywords,
                    "case_sensitive": self.config.case_sensitive,
                },
                guardrail_name=self.name,
            )

        # 2. Try DSPy-based analysis, fall back to simple matching
        if is_dspy_configured():
            try:
                result = self._program(
                    blocked_keywords=self.config.blocked_keywords,
                    user_input=input_text,
                    case_sensitive=self.config.case_sensitive,
                )

                is_allowed = (
                    not result.contains_blocked
                )  # Allowed if NO blocked keywords found

                reason = None
                if result.contains_blocked and result.matched_keywords:
                    matched = ", ".join(result.matched_keywords)
                    reason = f"Blocked keywords detected: {matched}"

                return GuardrailResult(
                    is_allowed=is_allowed,
                    reason=reason,
                    metadata={
                        "contains_blocked": result.contains_blocked,
                        "matched_keywords": result.matched_keywords or [],
                        "blocked_keywords": self.config.blocked_keywords,
                        "case_sensitive": self.config.case_sensitive,
                        "explanation": result.reason,
                        "method": "dspy",
                    },
                    guardrail_name=self.name,
                )
            except Exception:
                # Fall back to simple string matching if DSPy fails
                pass

        # 3. Simple string matching fallback
        contains_blocked, matched_keywords = simple_keyword_check(
            input_text,
            self.config.blocked_keywords or [],
            self.config.case_sensitive,
        )

        is_allowed = not contains_blocked
        reason = None
        if contains_blocked:
            matched = ", ".join(matched_keywords)
            reason = f"Blocked keywords detected: {matched}"

        return GuardrailResult(
            is_allowed=is_allowed,
            reason=reason,
            metadata={
                "contains_blocked": contains_blocked,
                "matched_keywords": matched_keywords,
                "blocked_keywords": self.config.blocked_keywords,
                "case_sensitive": self.config.case_sensitive,
                "method": "simple",
            },
            guardrail_name=self.name,
        )
