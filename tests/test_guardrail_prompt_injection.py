from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_prompt_injection_guardrail_type():
    guard = guardrail.PromptInjection(injection_patterns=["ignore previous"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "prompt_injection"
    assert guard.config.injection_patterns == ["ignore previous"]
