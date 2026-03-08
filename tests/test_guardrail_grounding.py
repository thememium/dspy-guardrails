from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_grounding_guardrail_type():
    guard = guardrail.Grounding(grounding_threshold=0.9)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "grounding"
    assert guard.config.grounding_threshold == 0.9
