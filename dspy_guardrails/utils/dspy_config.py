"""DSPy configuration utilities for guardrails."""

import dspy

from dspy_guardrails.core.config import GuardrailConfig
from dspy_guardrails.core.exceptions import DSPyConfigurationError


def configure_dspy_from_config(config: GuardrailConfig) -> None:
    """Configure DSPy for a guardrail using the globally configured guardrail LM.

    DSPy configuration is now handled globally. This function ensures that
    the globally configured guardrail LM is used for DSPy operations.

    Args:
        config: Guardrail configuration (no longer contains DSPy settings)

    Raises:
        DSPyConfigurationError: If DSPy configuration fails
    """
    try:
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
