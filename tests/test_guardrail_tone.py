from unittest.mock import MagicMock, patch

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_tone_guardrail_type():
    guard = guardrail.Tone(desired_tone="helpful", unwanted_tones=["sarcastic"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "tone"
    assert guard.config.desired_tone == "helpful"
    assert guard.config.unwanted_tones == ["sarcastic"]


def test_tone_check_not_configured():
    guard = guardrail.Tone(desired_tone="polite")

    with patch(
        "dspy_guardrails.guardrails.tone.is_dspy_configured", return_value=False
    ):
        result = guard.check("hello")

    assert result.is_allowed is False
    assert (
        result.reason
        == "DSPy is not properly configured. Please configure DSPy before using guardrails."
    )
    assert result.metadata == {"error": "DSPy not configured"}
    assert result.guardrail_name == "tone"


def test_tone_check_allowed():
    guard = guardrail.Tone(desired_tone="polite", unwanted_tones=["sarcastic"])
    mock_result = MagicMock()
    mock_result.is_desired_tone = True
    mock_result.detected_tones = ["polite", "friendly"]
    mock_result.reason = "Tone is polite and helpful."

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("Thanks so much for your help!")

    assert result.is_allowed is True
    assert result.reason is None
    assert result.metadata == {
        "detected_tones": ["polite", "friendly"],
        "desired_tone": "polite",
        "unwanted_tones": ["sarcastic"],
        "explanation": "Tone is polite and helpful.",
    }
    assert result.guardrail_name == "tone"


def test_tone_check_disallowed_with_reason():
    guard = guardrail.Tone(desired_tone="polite", unwanted_tones=["sarcastic"])
    mock_result = MagicMock()
    mock_result.is_desired_tone = False
    mock_result.detected_tones = ["sarcastic"]
    mock_result.reason = "The text is sarcastic."

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("Oh great, another meeting.")

    assert result.is_allowed is False
    assert result.reason == "The text is sarcastic."
    md = result.metadata or {}
    assert md["detected_tones"] == ["sarcastic"]
    assert md["desired_tone"] == "polite"
    assert md["unwanted_tones"] == ["sarcastic"]
    assert md["explanation"] == "The text is sarcastic."
    assert result.guardrail_name == "tone"


def test_tone_check_disallowed_fallback_reason():
    """When the LLM returns no reason, check() falls back to a default message."""
    guard = guardrail.Tone(desired_tone="polite", unwanted_tones=["rude"])
    mock_result = MagicMock()
    mock_result.is_desired_tone = False
    mock_result.detected_tones = None
    mock_result.reason = ""

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("Whatever.")

    assert result.is_allowed is False
    assert result.reason == "Content does not match the desired tone: polite"
    md = result.metadata or {}
    assert md["detected_tones"] == []
    assert md["explanation"] == ""
    assert result.guardrail_name == "tone"


def test_tone_check_exception():
    guard = guardrail.Tone(desired_tone="polite")

    with patch.object(guard, "_run_program", side_effect=RuntimeError("boom")):
        result = guard.check("hello")

    assert result.is_allowed is False
    assert result.reason == "Error during tone check: boom"
    assert result.metadata == {"error": "boom"}
    assert result.guardrail_name == "tone"
