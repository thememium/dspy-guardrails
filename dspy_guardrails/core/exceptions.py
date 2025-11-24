"""Custom exceptions for DSPy Guardrails."""


class GuardrailError(Exception):
    """Base exception for all guardrail-related errors."""

    pass


class ConfigurationError(GuardrailError):
    """Raised when there's an error in guardrail configuration."""

    pass


class DSPyConfigurationError(GuardrailError):
    """Raised when DSPy configuration fails."""

    pass


class GuardrailExecutionError(GuardrailError):
    """Raised when a guardrail execution fails."""

    pass


class ValidationError(GuardrailError):
    """Raised when input validation fails."""

    pass
