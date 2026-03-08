from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_toxicity_guardrail_type():
    guard = guardrail.Toxicity(toxicity_threshold=0.8)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "toxicity"
    assert guard.config.toxicity_threshold == 0.8
