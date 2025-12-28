"""Language detection and compliance guardrail implementation."""

from typing import List

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import LanguageGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


class GuardrailsLanguageSignature(dspy.Signature):
    """You are a language detection system.
    Identify the language of the input text and determine if it belongs to the allowed language list.

    The detected language should be returned as an ISO 639-1 code (e.g., 'en', 'fr', 'es')."""

    user_input: str = dspy.InputField(desc="The text content to analyze.")
    allowed_languages: List[str] = dspy.InputField(
        desc="List of allowed language codes (e.g., ['en', 'es'])."
    )
    detected_language_code: str = dspy.OutputField(
        desc="The detected ISO 639-1 language code of the input."
    )
    detected_language_name: str = dspy.OutputField(
        desc="The full name of the detected language."
    )
    is_allowed_language: bool = dspy.OutputField(
        desc="True if the detected language is in the allowed list, False otherwise."
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation of the language detection result."
    )


class LanguageGuardrail(BaseGuardrail):
    """Guardrail for ensuring content is in an allowed language."""

    def __init__(self, config: LanguageGuardrailConfig):
        """Initialize the language guardrail.

        Args:
            config: Configuration for the language guardrail
        """
        super().__init__(config)
        self.config: LanguageGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsLanguageSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "language"

    def _configure_dspy(self) -> None:
        """Configure DSPy for language guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text language is allowed.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if language is allowed
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
                allowed_languages=self.config.allowed_languages,
            )

            is_allowed = result.is_allowed_language
            reason = None
            if not is_allowed:
                reason = (
                    result.reason
                    or f"Language '{result.detected_language_name}' ({result.detected_language_code}) is not allowed."
                )

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "detected_language_code": result.detected_language_code,
                    "detected_language_name": result.detected_language_name,
                    "allowed_languages": self.config.allowed_languages,
                    "explanation": result.reason,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during language check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
