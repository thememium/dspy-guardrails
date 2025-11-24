"""PII detection guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import PiiGuardrailConfig
from dspy_guardrails.utils.dspy_config import configure_dspy_from_config


class GuardrailsPiiSignature(dspy.Signature):
    """You are a PII (Personally Identifiable Information) detection system.

    Your task is to analyze text and identify any personally identifiable information.
    PII includes information that can be used to identify, contact, or locate an individual.

    Common types of PII include:
    - Names (full names, first names, last names)
    - Email addresses
    - Phone numbers
    - Physical addresses
    - Social Security Numbers (SSN) or equivalent
    - Driver's license numbers
    - Passport numbers
    - Bank account numbers
    - Credit card numbers
    - IP addresses
    - Medical record numbers
    - Biometric data references
    - Any other information that could identify an individual

    Flag any content that contains PII, even if it's fictional or example data."""

    user_input: str = dspy.InputField(desc="The text content to analyze for PII.")
    pii_detected: bool = dspy.OutputField(
        desc="Boolean indicating if any PII was detected. True if PII found, False if no PII."
    )
    pii_types: Optional[List[str]] = dspy.OutputField(
        desc="List of PII types detected (e.g., 'email', 'phone', 'ssn'). Empty if no PII found."
    )
    pii_examples: Optional[List[str]] = dspy.OutputField(
        desc="Specific examples of PII found in the text. Empty if no PII found."
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation of why this content contains or doesn't contain PII."
    )


class PiiGuardrail(BaseGuardrail):
    """Guardrail for detecting Personally Identifiable Information (PII)."""

    def __init__(self, config: PiiGuardrailConfig):
        """Initialize the PII guardrail.

        Args:
            config: Configuration for the PII guardrail
        """
        super().__init__(config)
        self._program = dspy.ChainOfThought(GuardrailsPiiSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "pii"

    def _configure_dspy(self) -> None:
        """Configure DSPy for PII guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str) -> GuardrailResult:
        """Check if the input text contains personally identifiable information.

        Args:
            input_text: The text content to analyze

        Returns:
            GuardrailResult indicating if content contains PII
        """
        try:
            result = self._program(user_input=input_text)

            is_allowed = not result.pii_detected  # Allowed if NO PII detected

            reason = None
            if result.pii_detected:
                pii_types_str = ", ".join(result.pii_types or [])
                reason = f"PII detected: {pii_types_str}"

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "pii_detected": result.pii_detected,
                    "pii_types": result.pii_types or [],
                    "pii_examples": result.pii_examples or [],
                    "explanation": result.reason,
                    "allowed_pii_types": self.config.allowed_pii_types,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during PII check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
