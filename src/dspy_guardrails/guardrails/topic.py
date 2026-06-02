"""Topic compliance guardrail implementation.

Includes a fast, regex-based prefilter that runs before the DSPy LLM
call.  The prefilter is partial — it only handles ``blocked_topics``
(case-insensitive substring matching) which can be deterministically
detected. ``topic_scopes`` evaluation (which requires semantic
understanding) is left entirely to the DSPy LLM fallback.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import TopicGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)

# --------------------------------------------------------------------------- #
# ReDoS safety (mirrored from dspy_guardrails.guardrails.pii)                  #
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
# Prefilter result type                                                        #
# --------------------------------------------------------------------------- #


@dataclass
class _TopicMatch:
    """One regex prefilter hit for a blocked topic."""

    topic: str
    matched_text: str


# --------------------------------------------------------------------------- #
# Topic guardrail                                                              #
# --------------------------------------------------------------------------- #


class GuardrailsTopicSignature(dspy.Signature):
    """You are a content analysis system that determines if text stays on topic.

    Determine if the text stays within the defined topic scope. Flag any content that strays from the allowed topics."""

    topic_scopes: List[str] = dspy.InputField(
        desc="The defined topic scope or topics. A list of topics that are considered on topic."
    )
    blocked_topics: List[str] = dspy.InputField(
        desc="List of blocked topics or items to flag if mentioned in the content."
    )
    user_input: str = dspy.InputField(desc="The text content to analyze.")
    off_topic_reasons: Optional[List[str]] = dspy.OutputField(
        desc="List of reasons why the content is off topic, if applicable. Empty if on topic. A single word reason is sufficient."
    )
    is_on_topic: bool = dspy.OutputField(
        desc="Boolean indicating if the content stays on topic. True if on topic, False if off topic."
    )


class TopicGuardrail(BaseGuardrail):
    """Guardrail for checking if content stays within defined topic scopes.

    Runs a fast, deterministic substring prefilter against
    ``blocked_topics`` before delegating to a DSPy ChainOfThought
    program for nuanced ``topic_scopes`` evaluation.  When the
    prefilter finds a match it short-circuits with ``is_allowed=False``
    and ``method="regex_prefilter"``.  Otherwise the LLM handles the
    semantic on-topic check.
    """

    def __init__(self, config: TopicGuardrailConfig):
        """Initialize the topic guardrail.

        Args:
            config: Configuration for the topic guardrail
        """
        super().__init__(config)
        self.config: TopicGuardrailConfig = config  # Type hint for better type checking
        self._program = dspy.ChainOfThought(GuardrailsTopicSignature)

        # Compile blocked_topics into case-insensitive substring regexes
        # unless the user disabled the prefilter.
        self._compiled_blocked: List[Tuple[str, re.Pattern[str]]] = []
        if self.config.enable_blocked_topic_prefilter:
            for topic in self.config.blocked_topics or []:
                escaped = re.escape(topic)
                pat = re.compile(escaped, re.IGNORECASE)
                self._compiled_blocked.append((topic, pat))

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "topic"

    def _configure_dspy(self) -> None:
        """Configure DSPy for topic guardrail."""
        configure_dspy_from_config(self.config)

    # ------------------------------------------------------------------ #
    # Prefilter                                                            #
    # ------------------------------------------------------------------ #

    def _find_matches(self, text: str) -> List[_TopicMatch]:
        """Run all compiled blocked-topic patterns and return matches."""
        matches: List[_TopicMatch] = []
        for topic, pat in self._compiled_blocked:
            for m in pat.finditer(text):
                matches.append(_TopicMatch(topic=topic, matched_text=m.group(0)))
        return matches

    def _run_blocked_topic_prefilter(self, input_text: str) -> List[_TopicMatch]:
        """Run the blocked-topic prefilter.  Returns a (possibly empty)
        list of matches."""
        return self._find_matches(input_text)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text stays on topic.

        The blocked-topic prefilter runs first.  On a match the LLM is
        skipped and ``is_allowed=False``.  When no blocked topic is
        found, fall through to the DSPy LLM for ``topic_scopes``
        evaluation.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content is on topic
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

        # 1. Fast blocked-topic prefilter.  On any match, skip the LLM.
        matches = self._run_blocked_topic_prefilter(input_text)
        if matches:
            matched_topics = sorted({m.topic for m in matches})
            return GuardrailResult(
                is_allowed=False,
                reason=f"Blocked topic detected: {', '.join(matched_topics)}",
                metadata={
                    "method": "regex_prefilter",
                    "is_on_topic": False,
                    "off_topic_reasons": [
                        f"Blocked topic detected: {m.topic}" for m in matches
                    ],
                    "matched_blocked_topics": matched_topics,
                    "topic_scopes": self.config.topic_scopes,
                    "blocked_topics": self.config.blocked_topics,
                },
                guardrail_name=self.name,
            )

        # 2. LLM-based analysis via DSPy (evaluates topic_scopes).
        try:
            result = self._program(
                topic_scopes=self.config.topic_scopes,
                blocked_topics=self.config.blocked_topics,
                user_input=input_text,
            )

            is_allowed = result.is_on_topic
            reason = None
            if not is_allowed and result.off_topic_reasons:
                reason = "; ".join(result.off_topic_reasons)

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "off_topic_reasons": result.off_topic_reasons or [],
                    "topic_scopes": self.config.topic_scopes,
                    "blocked_topics": self.config.blocked_topics,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during topic check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
