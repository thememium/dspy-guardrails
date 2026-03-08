from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_pii_guardrail_type():
    guard = guardrail.Pii(allowed_pii_types=["email"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "pii"
    assert guard.config.allowed_pii_types == ["email"]
