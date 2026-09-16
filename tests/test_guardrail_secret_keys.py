from unittest.mock import MagicMock, patch

import pytest

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


AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
HEX_40 = "f3a9c1b7e2d84f60a5b3c9e17d2f84a06b19c3e7"


def test_is_unsafe_pattern_alternation_with_quantifier_rejected():
    assert _is_unsafe_pattern(r"(a|b)+") is True
    assert _is_unsafe_pattern(r"(ab|cd)*") is True


def test_custom_pattern_alternation_redos_rejected():
    with pytest.raises(ValueError, match="catastrophic backtracking"):
        guardrail.SecretKeys(custom_patterns=[{"name": "bad", "pattern": r"(a|a)*"}])


def test_is_unsafe_pattern_safe_shape_returns_false():
    """Patterns without a quantified group fall through both screens."""
    assert _is_unsafe_pattern(r"foo|bar") is False
    assert _is_unsafe_pattern(r"[a-z]{2,}") is False


def test_custom_patterns_compiled_with_labels():
    guard = guardrail.SecretKeys(
        custom_patterns=[
            {
                "name": "corp_token",
                "pattern": r"CORP-[A-Z0-9]{12}",
                "label": "Corporate Token",
            },
            {"name": "plain", "pattern": r"PLAIN[0-9]{4}"},
        ]
    )

    assert set(guard._compiled_custom) == {"corp_token", "plain"}
    assert guard._custom_labels == {"corp_token": "Corporate Token", "plain": "plain"}


def test_find_matches_builtin_catalog_hit():
    guard = guardrail.SecretKeys()

    matches = guard._find_matches(f"use {AWS_KEY} for deployment")

    assert [m.slug for m in matches] == ["aws_access_key"]
    assert matches[0].matched_text == AWS_KEY
    assert matches[0].entropy == pytest.approx(_shannon_entropy(AWS_KEY))


def test_find_matches_custom_pattern_hit():
    guard = guardrail.SecretKeys(
        custom_patterns=[{"name": "corp", "pattern": r"CORP-[A-Z0-9]{12}"}]
    )

    matches = guard._find_matches("id CORP-AB12CD34EF56 here")

    assert [m.slug for m in matches] == ["custom:corp"]
    assert matches[0].matched_text == "CORP-AB12CD34EF56"
    assert matches[0].entropy > 0


def test_find_matches_user_prefix_above_threshold():
    guard = guardrail.SecretKeys(
        key_patterns=["sk-"], entropy_threshold=3.5, enable_regex_prefilter=False
    )
    text = "sk-" + HEX_40

    matches = guard._find_matches(text)

    assert len(matches) == 1
    assert matches[0].slug == "user:sk-"
    assert matches[0].matched_text == text
    assert matches[0].entropy >= 3.5


def test_find_matches_user_prefix_below_threshold_discarded():
    guard = guardrail.SecretKeys(
        key_patterns=["sk-"], entropy_threshold=3.5, enable_regex_prefilter=False
    )

    assert guard._find_matches("sk-" + "a" * 40) == []


def test_run_regex_prefilter_passthrough():
    guard = guardrail.SecretKeys()

    assert guard._run_regex_prefilter("nothing suspicious here") == []
    matches = guard._run_regex_prefilter(f"key {AWS_KEY}")

    assert [m.slug for m in matches] == ["aws_access_key"]


def test_check_returns_error_when_dspy_not_configured():
    guard = guardrail.SecretKeys()

    with patch(
        "dspy_guardrails.guardrails.secret_keys.is_dspy_configured",
        return_value=False,
    ):
        result = guard.check("hello world")

    assert result.is_allowed is False
    assert result.reason == (
        "DSPy is not properly configured. Please configure DSPy before using guardrails."
    )
    assert result.metadata == {"error": "DSPy not configured"}
    assert result.guardrail_name == "secret_keys"


def test_check_prefilter_short_circuit_builtin():
    guard = guardrail.SecretKeys()

    result = guard.check(f"leaked {AWS_KEY} in logs")

    assert result.is_allowed is False
    assert "aws_access_key" in (result.reason or "")
    assert result.guardrail_name == "secret_keys"
    md = result.metadata or {}
    assert md["method"] == "regex_prefilter"
    assert md["secrets_detected"] is True
    assert md["detected_secrets"] == [AWS_KEY]
    assert md["matches"] == [
        {
            "slug": "aws_access_key",
            "matched_text": AWS_KEY,
            "entropy": round(_shannon_entropy(AWS_KEY), 3),
        }
    ]


def test_check_prefilter_runs_custom_patterns_when_builtin_disabled():
    guard = guardrail.SecretKeys(
        enable_regex_prefilter=False,
        custom_patterns=[{"name": "corp", "pattern": r"CORP-[A-Z0-9]{12}"}],
    )

    result = guard.check("token CORP-AB12CD34EF56")

    md = result.metadata or {}
    assert md["method"] == "regex_prefilter"
    assert md["detected_secrets"] == ["CORP-AB12CD34EF56"]
    assert md["matches"][0]["slug"] == "custom:corp"
    assert "custom:corp" in (result.reason or "")


def test_check_llm_path_allows_clean_text():
    guard = guardrail.SecretKeys()
    mock_result = MagicMock(
        secrets_detected=False, detected_secrets=[], secret_types=[], risk_level="low"
    )

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("an ordinary sentence about the weather")

    assert result.is_allowed is True
    assert result.reason is None
    assert result.guardrail_name == "secret_keys"
    assert result.metadata == {
        "secrets_detected": False,
        "detected_secrets": [],
        "secret_types": [],
        "risk_level": "low",
        "key_patterns": guard._key_patterns,
        "entropy_threshold": 4.0,
        "method": "dspy",
    }


def test_check_llm_path_blocks_without_details_when_list_empty():
    guard = guardrail.SecretKeys()
    mock_result = MagicMock(
        secrets_detected=True,
        detected_secrets=[],
        secret_types=["api_key"],
        risk_level="high",
    )

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("innocuous text")

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md["detected_secrets"] == []
    assert md["secret_types"] == ["api_key"]
    assert md["method"] == "dspy"


def test_check_llm_path_truncates_detected_secrets_in_reason():
    guard = guardrail.SecretKeys()
    secrets = ["sk-aaa111", "sk-bbb222", "sk-ccc333", "sk-ddd444", "sk-eee555"]
    mock_result = MagicMock(
        secrets_detected=True,
        detected_secrets=secrets,
        secret_types=["api_key"],
        risk_level="critical",
    )

    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("please analyze this text")

    assert result.is_allowed is False
    assert result.reason == (
        "Potential secrets detected: sk-aaa111, sk-bbb222, sk-ccc333 (+2 more)"
    )
    md = result.metadata or {}
    assert md["detected_secrets"] == secrets
    assert md["risk_level"] == "critical"
    assert md["method"] == "dspy"


def test_check_llm_exception_returns_error_result():
    guard = guardrail.SecretKeys()

    with patch.object(guard, "_run_program", side_effect=RuntimeError("boom")):
        result = guard.check("no secrets in this sentence")

    assert result.is_allowed is False
    assert result.reason == "Error during secret detection: boom"
    assert result.metadata == {"error": "boom", "method": "dspy"}
    assert result.guardrail_name == "secret_keys"
