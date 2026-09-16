"""Tests for dspy_guardrails.utils.dspy_config."""

from unittest.mock import patch

import dspy
import pytest

from dspy_guardrails.core.config import GuardrailConfig, get_guardrail_lm
from dspy_guardrails.core.exceptions import DSPyConfigurationError
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


def test_configure_dspy_from_config_applies_guardrail_lm():
    configure_dspy_from_config(GuardrailConfig())
    assert dspy.settings.lm is get_guardrail_lm()


def test_configure_dspy_from_config_wraps_errors():
    original = ValueError("no lm configured")
    with pytest.raises(
        DSPyConfigurationError, match="Failed to configure DSPy"
    ) as excinfo:
        with patch(
            "dspy_guardrails.core.config.get_guardrail_lm", side_effect=original
        ):
            configure_dspy_from_config(GuardrailConfig())
    assert excinfo.value.__cause__ is original


def test_is_dspy_configured_true_when_lm_available():
    assert is_dspy_configured() is True


def test_is_dspy_configured_false_when_unconfigured():
    with patch(
        "dspy_guardrails.core.config.get_guardrail_lm",
        side_effect=ValueError("Guardrails not configured"),
    ):
        assert is_dspy_configured() is False
