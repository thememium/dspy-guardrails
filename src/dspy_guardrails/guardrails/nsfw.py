"""NSFW detection guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import NsfwGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


class GuardrailsNsfwSignature(dspy.Signature):
    """You are a content moderation assistant.
    Your task is to analyze text and determine if it contains NSFW (Not Safe For Work) content.

    Flag any content that matches these criteria."""

    nsfw_content_types: List[str] = dspy.InputField(
        desc="List of NSFW content types to check for."
    )
    user_input: str = dspy.InputField(desc="The text content to analyze.")
    nsfw_reasons: Optional[List[str]] = dspy.OutputField(
        desc="List of reasons why the content is considered NSFW, if applicable. Empty if safe. A single word reason is sufficient."
    )
    is_input_nsfw: bool = dspy.OutputField(
        desc="Boolean indicating if the content is NSFW. True if NSFW, False if safe."
    )


class NsfwGuardrail(BaseGuardrail):
    """Guardrail for detecting NSFW (Not Safe For Work) content."""

    def __init__(self, config: NsfwGuardrailConfig):
        """Initialize the NSFW guardrail.

        Args:
            config: Configuration for the NSFW guardrail
        """
        super().__init__(config)
        self.config: NsfwGuardrailConfig = config  # Type hint for better type checking
        self._program = dspy.ChainOfThought(GuardrailsNsfwSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "nsfw"

    def _configure_dspy(self) -> None:
        """Configure DSPy for NSFW guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains NSFW content.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content is NSFW
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
                nsfw_content_types=self.config.nsfw_content_types,
                user_input=input_text,
            )

            is_allowed = not result.is_input_nsfw  # Allowed if NOT NSFW
            reason = None
            if result.is_input_nsfw and result.nsfw_reasons:
                reason = "; ".join(result.nsfw_reasons)

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "nsfw_reasons": result.nsfw_reasons or [],
                    "nsfw_content_types": self.config.nsfw_content_types,
                    "sensitivity_level": self.config.sensitivity_level,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during NSFW check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
