"""DSPy configuration utilities for guardrails."""

import dspy

from dspy_guardrails.core.config import GuardrailConfig
from dspy_guardrails.core.exceptions import DSPyConfigurationError
from dspy_guardrails.utils.adapters import GuardrailJSONAdapter


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

        # Prefer the JSONAdapter by default: it parses the typed outputs of
        # guardrail signatures (bools, lists, floats) in a single pass.
        # The default ChatAdapter fallback path re-issues the whole LM call
        # through JSONAdapter whenever its first parse fails, doubling LM
        # invocations for JSON-responding models. Respect an adapter the
        # user has configured globally.
        config_kwargs = {"lm": lm}
        if dspy.settings.adapter is None:
            config_kwargs["adapter"] = GuardrailJSONAdapter()
        dspy.configure(**config_kwargs)

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
