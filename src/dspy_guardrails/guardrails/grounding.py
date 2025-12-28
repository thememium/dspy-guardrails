"""Grounding and hallucination detection guardrail implementation."""

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import GroundingGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


class GuardrailsGroundingSignature(dspy.Signature):
    """You are a fact-checking system.
    Determine if the provided 'answer' is grounded in and supported by the 'context'.

    Flag any information in the answer that is NOT present in or cannot be reasonably inferred from the context.
    Provide a grounding score between 0.0 and 1.0, where 1.0 means perfectly grounded."""

    context: str = dspy.InputField(desc="The reference source text or context.")
    answer: str = dspy.InputField(
        desc="The statement or answer to verify against the context."
    )
    grounding_score: float = dspy.OutputField(
        desc="A score between 0.0 and 1.0 indicating how well the answer is grounded in the context."
    )
    is_grounded: bool = dspy.OutputField(
        desc="True if the answer is sufficiently grounded in the context, False if it contains hallucinations."
    )
    hallucinations: list[str] = dspy.OutputField(
        desc="List of specific claims in the answer that are not supported by the context."
    )
    reason: str = dspy.OutputField(desc="Explanation for the grounding assessment.")


class GroundingGuardrail(BaseGuardrail):
    """Guardrail for detecting hallucinations and ensuring factual grounding."""

    def __init__(self, config: GroundingGuardrailConfig):
        """Initialize the grounding guardrail.

        Args:
            config: Configuration for the grounding guardrail
        """
        super().__init__(config)
        self.config: GroundingGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsGroundingSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "grounding"

    def _configure_dspy(self) -> None:
        """Configure DSPy for grounding guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text is grounded in the provided context.

        Args:
            input_text: The answer or statement to check
            **kwargs: Must include 'context' for grounding check

        Returns:
            GuardrailResult indicating if content is grounded
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

        context = kwargs.get("context")
        if not context:
            return GuardrailResult(
                is_allowed=False,
                reason="Grounding check requires 'context' to be provided in kwargs.",
                metadata={"error": "Missing context"},
                guardrail_name=self.name,
            )

        try:
            result = self._program(context=context, answer=input_text)

            is_flagged = (
                not result.is_grounded
                or result.grounding_score < self.config.grounding_threshold
            )
            is_allowed = not is_flagged

            reason = None
            if is_flagged:
                hallucination_msg = ""
                if result.hallucinations:
                    hallucination_msg = (
                        f" Hallucinations: {', '.join(result.hallucinations)}"
                    )
                reason = (
                    result.reason
                    or f"Factual grounding failed (score: {result.grounding_score:.2f})"
                ) + hallucination_msg

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "grounding_score": result.grounding_score,
                    "is_grounded": result.is_grounded,
                    "hallucinations": result.hallucinations or [],
                    "explanation": result.reason,
                    "threshold": self.config.grounding_threshold,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during grounding check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
