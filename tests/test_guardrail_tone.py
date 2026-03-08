from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_tone_guardrail_type():
    guard = guardrail.Tone(desired_tone="helpful", unwanted_tones=["sarcastic"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "tone"
    assert guard.config.desired_tone == "helpful"
    assert guard.config.unwanted_tones == ["sarcastic"]
