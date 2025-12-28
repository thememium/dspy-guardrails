"""Gibberish detection guardrail implementation."""

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import GibberishGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


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
    """Guardrail for detecting nonsensical or random text."""

    def __init__(self, config: GibberishGuardrailConfig):
        """Initialize the gibberish guardrail.

        Args:
            config: Configuration for the gibberish guardrail
        """
        super().__init__(config)
        self.config: GibberishGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsGibberishSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "gibberish"

    def _configure_dspy(self) -> None:
        """Configure DSPy for gibberish guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text is gibberish.

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
