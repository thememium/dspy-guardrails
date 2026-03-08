from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_language_guardrail_type():
    guard = guardrail.Language(allowed_languages=["en", "es"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "language"
    assert guard.config.allowed_languages == ["en", "es"]
