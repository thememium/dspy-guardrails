"""Secret keys detection guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import SecretKeysGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


class GuardrailsSecretKeysSignature(dspy.Signature):
    """You are a security system that detects secret keys, API tokens, and other sensitive credentials in text.

    Your task is to identify potentially leaked secrets that should not be exposed in logs, code, or user content.

    Common types of secrets to detect:
    - API keys and tokens (AWS, OpenAI, GitHub, etc.)
    - Private keys and certificates
    - Passwords and authentication credentials
    - Database connection strings
    - Encryption keys
    - Access tokens and bearer tokens
    - Webhook secrets
    - Any other sensitive authentication material

    Look for patterns like:
    - Common prefixes (sk-, pk_, AKIA, ghp_, xox, etc.)
    - Long alphanumeric strings that look like keys
    - Base64-encoded data that might be secrets
    - Environment variable names containing secrets
    - Code comments or logs that accidentally include secrets

    Consider entropy - random-looking strings are more likely to be secrets.
    Be cautious about false positives - not every long string is a secret."""

    key_patterns: List[str] = dspy.InputField(
        desc="List of known key patterns or prefixes to look for."
    )
    entropy_threshold: float = dspy.InputField(
        desc="Minimum entropy threshold for detecting potential secrets (0-10)."
    )
    user_input: str = dspy.InputField(
        desc="The text content to analyze for secret keys."
    )
    detected_secrets: Optional[List[str]] = dspy.OutputField(
        desc="List of detected secret strings. Empty if no secrets found."
    )
    secret_types: Optional[List[str]] = dspy.OutputField(
        desc="List of secret types detected (e.g., 'api_key', 'password', 'token'). Empty if no secrets found."
    )
    risk_level: str = dspy.OutputField(
        desc="Risk assessment: 'low', 'medium', 'high', or 'critical'."
    )
    secrets_detected: bool = dspy.OutputField(
        desc="Boolean indicating if any secrets were detected. True if secrets found, False if clean."
    )


class SecretKeysGuardrail(BaseGuardrail):
    """Guardrail for detecting secret keys and sensitive credentials."""

    def __init__(self, config: SecretKeysGuardrailConfig):
        """Initialize the secret keys guardrail.

        Args:
            config: Configuration for the secret keys guardrail
        """
        super().__init__(config)
        self.config: SecretKeysGuardrailConfig = (
            config  # Type hint for better type checking
        )
        self._program = dspy.ChainOfThought(GuardrailsSecretKeysSignature)

        # Default key patterns if not specified
        self._key_patterns = self.config.key_patterns or [
            "sk-",
            "sk_",
            "pk_",
            "pk-",
            "ghp_",
            "AKIA",
            "xox",
            "SG.",
            "hf_",
            "api-",
            "token",
            "secret",
            "password",
            "key",
            "Bearer ",
            "Authorization:",
            "API_KEY",
            "SECRET_KEY",
        ]

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "secret_keys"

    def _configure_dspy(self) -> None:
        """Configure DSPy for secret keys guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains secret keys or sensitive credentials.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content contains secrets
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
                key_patterns=self._key_patterns,
                entropy_threshold=self.config.entropy_threshold,
                user_input=input_text,
            )

            is_allowed = not result.secrets_detected  # Allowed if NO secrets detected

            reason = None
            if result.secrets_detected and result.detected_secrets:
                detected = ", ".join(result.detected_secrets[:3])  # Show first 3
                if len(result.detected_secrets) > 3:
                    detected += f" (+{len(result.detected_secrets) - 3} more)"
                reason = f"Potential secrets detected: {detected}"

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "secrets_detected": result.secrets_detected,
                    "detected_secrets": result.detected_secrets or [],
                    "secret_types": result.secret_types or [],
                    "risk_level": result.risk_level,
                    "key_patterns": self._key_patterns,
                    "entropy_threshold": self.config.entropy_threshold,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during secret detection: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
