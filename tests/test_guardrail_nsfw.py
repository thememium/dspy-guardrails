from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_nsfw_guardrail_type():
    guard = guardrail.Nsfw(sensitivity_level="high")

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "nsfw"
    assert guard.config.sensitivity_level == "high"
    assert guard.config.nsfw_content_types
