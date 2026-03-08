from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_gibberish_guardrail_type():
    guard = guardrail.Gibberish(prob_threshold=0.7)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "gibberish"
    assert guard.config.prob_threshold == 0.7
