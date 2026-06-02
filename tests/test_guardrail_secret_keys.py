from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail
from dspy_guardrails.guardrails.secret_keys import (
    SECRET_KEY_PATTERNS,
    _is_unsafe_pattern,
    _shannon_entropy,
)


def test_secret_keys_guardrail_type():
    guard = guardrail.SecretKeys(key_patterns=["sk-"], entropy_threshold=3.5)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "secret_keys"
    assert guard.config.key_patterns == ["sk-"]
    assert guard.config.entropy_threshold == 3.5


def test_secret_keys_default_config_enables_prefilter():
    guard = guardrail.SecretKeys()

    assert guard.config.enable_regex_prefilter is True
    assert set(guard._compiled_patterns) == set(SECRET_KEY_PATTERNS)


def test_prefilter_disabled_no_compiled_patterns():
    guard = guardrail.SecretKeys(enable_regex_prefilter=False)

    assert guard._compiled_patterns == {}


def test_custom_pattern_redos_rejected():
    """(a+)+ is the canonical ReDoS shape. Must be rejected at config time."""
    import pytest

    with pytest.raises(ValueError, match="catastrophic backtracking"):
        guardrail.SecretKeys(custom_patterns=[{"name": "bad", "pattern": r"(a+)+"}])


def test_shannon_entropy_single_char():
    assert _shannon_entropy("aaaaa") == 0.0


def test_shannon_entropy_empty():
    assert _shannon_entropy("") == 0.0


def test_is_unsafe_pattern_nested_quantifier():
    assert _is_unsafe_pattern(r"(a+)+") is True
    assert _is_unsafe_pattern(r"(a*)*") is True


def test_is_unsafe_pattern_safe_examples():
    assert _is_unsafe_pattern(r"AKIA[0-9A-Z]{16}") is False
    assert _is_unsafe_pattern(r"\bsk-[A-Za-z0-9]{20,}") is False

