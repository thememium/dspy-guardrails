from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_secret_keys_guardrail_type():
    guard = guardrail.SecretKeys(key_patterns=["sk-"], entropy_threshold=3.5)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "secret_keys"
    assert guard.config.key_patterns == ["sk-"]
    assert guard.config.entropy_threshold == 3.5
