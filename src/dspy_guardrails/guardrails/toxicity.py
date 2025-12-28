"""Toxicity detection guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import ToxicityGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


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
    """Guardrail for detecting toxic and harmful language."""

    def __init__(self, config: ToxicityGuardrailConfig):
        """Initialize the toxicity guardrail.

        Args:
            config: Configuration for the toxicity guardrail
        """
        super().__init__(config)
        self.config: ToxicityGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsToxicitySignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "toxicity"

    def _configure_dspy(self) -> None:
        """Configure DSPy for toxicity guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains toxic content.

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
