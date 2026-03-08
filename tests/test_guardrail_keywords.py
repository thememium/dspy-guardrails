from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_keywords_guardrail_type():
    guard = guardrail.Keywords(blocked_keywords=["secret"], case_sensitive=True)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "keywords"
    assert guard.config.blocked_keywords == ["secret"]
    assert guard.config.case_sensitive is True
