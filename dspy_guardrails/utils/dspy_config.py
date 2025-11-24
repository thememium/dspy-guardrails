"""DSPy configuration utilities for guardrails."""

import os

import dspy

from dspy_guardrails.core.config import GuardrailConfig
from dspy_guardrails.core.exceptions import DSPyConfigurationError


def configure_dspy_from_config(config: GuardrailConfig) -> None:
    """Configure DSPy using the provided configuration.

    Args:
        config: Guardrail configuration containing DSPy settings

    Raises:
        DSPyConfigurationError: If DSPy configuration fails
    """
    try:
        # Get API key from environment
        api_key = os.getenv(config.api_key_env_var)
        if not api_key:
            raise DSPyConfigurationError(
                f"API key not found in environment variable '{config.api_key_env_var}'"
            )

        # Configure the language model
        lm = dspy.LM(
            config.model,
            api_key=api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            cache=config.cache_enabled,
            timeout=config.timeout_seconds,
        )

        # Configure DSPy
        dspy.configure(lm=lm)

    except Exception as e:
        raise DSPyConfigurationError(f"Failed to configure DSPy: {e}") from e


def get_default_dspy_config() -> GuardrailConfig:
    """Get default DSPy configuration.

    Returns:
        Default GuardrailConfig with sensible defaults
    """
    return GuardrailConfig()


def is_dspy_configured() -> bool:
    """Check if DSPy is already configured.

    Returns:
        True if DSPy has a language model configured, False otherwise
    """
    try:
        # Try to access the configured LM
        lm = dspy.settings.lm
        return lm is not None
    except AttributeError:
        return False
