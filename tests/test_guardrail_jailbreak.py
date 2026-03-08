from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_jailbreak_guardrail_type():
    guard = guardrail.Jailbreak(detection_threshold=0.9)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "jailbreak"
    assert guard.config.detection_threshold == 0.9
