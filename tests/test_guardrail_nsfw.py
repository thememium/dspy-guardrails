from unittest.mock import MagicMock, patch

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_nsfw_guardrail_type():
    guard = guardrail.Nsfw(sensitivity_level="high")

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "nsfw"
    assert guard.config.sensitivity_level == "high"
    assert guard.config.nsfw_content_types


def test_nsfw_check_not_configured():
    guard = guardrail.Nsfw()

    with patch(
        "dspy_guardrails.guardrails.nsfw.is_dspy_configured", return_value=False
    ):
        result = guard.check("hello")

    assert result.is_allowed is False
    assert (
        result.reason
        == "DSPy is not properly configured. Please configure DSPy before using guardrails."
    )
    assert result.metadata == {"error": "DSPy not configured"}
    assert result.guardrail_name == "nsfw"


def test_nsfw_check_allowed():
    guard = guardrail.Nsfw(sensitivity_level="medium")
    mock_result = MagicMock()
    mock_result.is_input_nsfw = False
    mock_result.nsfw_reasons = []

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("Have a great day!")

    assert result.is_allowed is True
    assert result.reason is None
    md = result.metadata or {}
    assert md["nsfw_reasons"] == []
    assert md["nsfw_content_types"] == guard.config.nsfw_content_types
    assert md["sensitivity_level"] == "medium"
    assert result.guardrail_name == "nsfw"


def test_nsfw_check_disallowed_with_reasons():
    guard = guardrail.Nsfw(sensitivity_level="high")
    mock_result = MagicMock()
    mock_result.is_input_nsfw = True
    mock_result.nsfw_reasons = ["explicit", "harassment"]

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("bad text")

    assert result.is_allowed is False
    assert result.reason == "explicit; harassment"
    md = result.metadata or {}
    assert md["nsfw_reasons"] == ["explicit", "harassment"]
    assert md["sensitivity_level"] == "high"
    assert result.guardrail_name == "nsfw"


def test_nsfw_check_disallowed_without_reasons():
    """Flagged content with no reasons yields reason=None and empty metadata list."""
    guard = guardrail.Nsfw()
    mock_result = MagicMock()
    mock_result.is_input_nsfw = True
    mock_result.nsfw_reasons = None

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("bad text")

    assert result.is_allowed is False
    assert result.reason is None
    md = result.metadata or {}
    assert md["nsfw_reasons"] == []
    assert result.guardrail_name == "nsfw"


def test_nsfw_check_exception():
    guard = guardrail.Nsfw()

    with patch.object(guard, "_run_program", side_effect=RuntimeError("boom")):
        result = guard.check("hello")

    assert result.is_allowed is False
    assert result.reason == "Error during NSFW check: boom"
    assert result.metadata == {"error": "boom"}
    assert result.guardrail_name == "nsfw"
