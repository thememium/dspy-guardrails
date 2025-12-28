"""Tone and sentiment guardrail implementation."""

from typing import List

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import ToneGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


class GuardrailsToneSignature(dspy.Signature):
    """You are a tone and sentiment analysis system.
    Your task is to analyze the input text's tone and determine if it matches the desired tone or contains unwanted tones.

    Unwanted tones include things like aggressiveness, rudeness, sarcasm, or offensiveness."""

    user_input: str = dspy.InputField(desc="The text content to analyze.")
    desired_tone: str = dspy.InputField(desc="The desired tone for the content.")
    unwanted_tones: List[str] = dspy.InputField(
        desc="List of tones that are not allowed."
    )

    detected_tones: List[str] = dspy.OutputField(
        desc="List of tones identified in the text (e.g., 'polite', 'sarcastic', 'aggressive')."
    )
    is_desired_tone: bool = dspy.OutputField(
        desc="True if the text matches the desired tone and doesn't contain unwanted tones."
    )
    reason: str = dspy.OutputField(desc="Brief explanation of the tone assessment.")


class ToneGuardrail(BaseGuardrail):
    """Guardrail for ensuring content matches building tone guidelines."""

    def __init__(self, config: ToneGuardrailConfig):
        """Initialize the tone guardrail.

        Args:
            config: Configuration for the tone guardrail
        """
        super().__init__(config)
        self.config: ToneGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsToneSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "tone"

    def _configure_dspy(self) -> None:
        """Configure DSPy for tone guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text matches the desired tone.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if tone is acceptable
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
                user_input=input_text,
                desired_tone=self.config.desired_tone,
                unwanted_tones=self.config.unwanted_tones,
            )

            is_allowed = result.is_desired_tone
            reason = None
            if not is_allowed:
                reason = (
                    result.reason
                    or f"Content does not match the desired tone: {self.config.desired_tone}"
                )

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "detected_tones": result.detected_tones or [],
                    "desired_tone": self.config.desired_tone,
                    "unwanted_tones": self.config.unwanted_tones,
                    "explanation": result.reason,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during tone check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
