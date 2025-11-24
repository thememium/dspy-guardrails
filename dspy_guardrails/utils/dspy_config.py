"""DSPy configuration utilities for guardrails."""

import os

import dspy

from dspy_guardrails.core.config import GuardrailConfig
from dspy_guardrails.core.exceptions import DSPyConfigurationError


def configure_dspy_from_config(config: GuardrailConfig) -> None:
    """Configure DSPy for a specific guardrail using the provided configuration.

    If config.model is provided, creates a temporary LM for this guardrail.
    Otherwise, uses the globally configured guardrail LM.

    Args:
        config: Guardrail configuration containing DSPy settings

    Raises:
        DSPyConfigurationError: If DSPy configuration fails
    """
    try:
        if config.model is not None:
            # Get API key from environment
            api_key = os.getenv(config.api_key_env_var)
            if not api_key:
                raise DSPyConfigurationError(
                    f"API key not found in environment variable '{config.api_key_env_var}'"
                )

            # Configure the language model
            lm = dspy.LM(
                config.model,  # We know this is not None here
                api_key=api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                cache=config.cache_enabled,
                timeout=config.timeout_seconds,
            )

            # Configure DSPy with this specific LM
            dspy.configure(lm=lm)
        else:
            # Use the globally configured guardrail LM
            from dspy_guardrails.core.config import get_guardrail_lm

            lm = get_guardrail_lm()
            dspy.configure(lm=lm)

    except Exception as e:
        raise DSPyConfigurationError(f"Failed to configure DSPy: {e}") from e


def is_dspy_configured() -> bool:
    """Check if guardrails are configured with a language model.

    Returns:
        True if guardrails have a language model configured, False otherwise
    """
    try:
        from dspy_guardrails.core.config import get_guardrail_lm

        get_guardrail_lm()
        return True
    except ValueError:
        return False
