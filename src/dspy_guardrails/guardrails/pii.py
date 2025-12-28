"""PII detection guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import PiiGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


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

    Flag any content that contains PII, even if it's fictional or example data.
    If 'allowed_pii_types' is provided, do not flag those specific types as pii_detected,
    but still list them in pii_types and pii_examples."""

    user_input: str = dspy.InputField(desc="The text content to analyze for PII.")
    allowed_pii_types: List[str] = dspy.InputField(
        desc="List of PII types that are allowed and should not be flagged."
    )
    pii_types: Optional[List[str]] = dspy.OutputField(
        desc="List of all PII types detected (e.g., 'email', 'phone', 'ssn')."
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation of why this content contains or doesn't contain non-allowed PII."
    )
    pii_examples: Optional[List[str]] = dspy.OutputField(
        desc="Specific examples of PII found in the text."
    )
    pii_detected: bool = dspy.OutputField(
        desc="True if any PII NOT in allowed_pii_types was detected, False otherwise."
    )


class PiiGuardrail(BaseGuardrail):
    """Guardrail for detecting Personally Identifiable Information (PII)."""

    def __init__(self, config: PiiGuardrailConfig):
        """Initialize the PII guardrail.

        Args:
            config: Configuration for the PII guardrail
        """
        super().__init__(config)
        self.config: PiiGuardrailConfig = config  # Type hint for better type checking
        self._program = dspy.ChainOfThought(GuardrailsPiiSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "pii"

    def _configure_dspy(self) -> None:
        """Configure DSPy for PII guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains personally identifiable information.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content contains PII
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
                allowed_pii_types=self.config.allowed_pii_types,
            )

            is_allowed = (
                not result.pii_detected
            )  # Allowed if NO non-allowed PII detected

            reason = None
            if result.pii_detected:
                # Find which types triggered the detection (those not in allowed_pii_types)
                detected_types = result.pii_types or []
                forbidden_types = [
                    t
                    for t in detected_types
                    if t not in (self.config.allowed_pii_types or [])
                ]
                if forbidden_types:
                    reason = f"PII detected: {', '.join(forbidden_types)}"
                else:
                    # Fallback if LLM flagged pii_detected but everything seems allowed
                    reason = result.reason or "PII detected"

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
