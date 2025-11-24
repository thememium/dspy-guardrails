"""Keyword filtering guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import KeywordsGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


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
    contains_blocked: bool = dspy.OutputField(
        desc="Boolean indicating if the text contains any blocked keywords. True if blocked content found, False if clean."
    )
    matched_keywords: Optional[List[str]] = dspy.OutputField(
        desc="List of blocked keywords that were found in the text. Empty if no matches."
    )
    reason: str = dspy.OutputField(
        desc="Explanation of why the content was flagged or why it passed the filter."
    )


class KeywordsGuardrail(BaseGuardrail):
    """Guardrail for filtering content based on blocked keywords."""

    def __init__(self, config: KeywordsGuardrailConfig):
        """Initialize the keywords guardrail.

        Args:
            config: Configuration for the keywords guardrail
        """
        super().__init__(config)
        self.config: KeywordsGuardrailConfig = (
            config  # Type hint for better type checking
        )
        self._program = dspy.ChainOfThought(GuardrailsKeywordsSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "keywords"

    def _configure_dspy(self) -> None:
        """Configure DSPy for keywords guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str) -> GuardrailResult:
        """Check if the input text contains blocked keywords.

        Args:
            input_text: The text content to analyze

        Returns:
            GuardrailResult indicating if content contains blocked keywords
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

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
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during keyword check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
