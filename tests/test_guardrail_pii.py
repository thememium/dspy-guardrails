"""Tests for the PII guardrail and its regex prefilter.

The prefilter is fully deterministic, so most tests can run without
invoking the DSPy LLM. The few tests that exercise the DSPy fallback
rely on the session-scoped ``configure_guardrails`` fixture in
``conftest.py``.
"""

import pytest

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.guardrails.pii import (
    PII_PATTERNS,
    REDACTED_PLACEHOLDER,
    _is_unsafe_pattern,
)

# --------------------------------------------------------------------------- #
# Construction / config                                                        #
# --------------------------------------------------------------------------- #


def test_pii_guardrail_type():
    guard = guardrail.Pii(allowed_pii_types=["email"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "pii"
    assert guard.config.allowed_pii_types == ["email"]


def test_pii_default_config_enables_prefilter():
    """Prefilter must be on by default with the built-in presets loaded."""
    guard = guardrail.Pii()

    assert guard.config.enable_regex_prefilter is True
    assert set(guard._compiled_builtins) == set(PII_PATTERNS)
    for slug in PII_PATTERNS:
        assert guard._builtin_actions[slug] == "redact"


def test_pii_allowed_pii_types_excludes_presets():
    """Legacy ``allowed_pii_types`` removes types from the prefilter."""
    guard = guardrail.Pii(allowed_pii_types=["email"])

    assert "email" not in guard._compiled_builtins
    # Other presets still loaded.
    assert "phone" in guard._compiled_builtins
    assert "ssn" in guard._compiled_builtins


def test_pii_actions_override_default_action():
    guard = guardrail.Pii(pii_actions={"ssn": "block", "email": "redact"})

    assert guard._builtin_actions["ssn"] == "block"
    assert guard._builtin_actions["email"] == "redact"
    # Unspecified presets default to their catalog default ("redact").
    assert guard._builtin_actions["phone"] == "redact"


def test_pii_custom_patterns_compile():
    guard = guardrail.Pii(
        custom_patterns=[
            {
                "name": "aws_key",
                "pattern": r"AKIA[0-9A-Z]{16}",
                "action": "block",
                "label": "AWS Key",
            }
        ]
    )

    assert "aws_key" in guard._compiled_custom
    assert guard._custom_actions["aws_key"] == ("block", "AWS Key")


def test_pii_custom_patterns_default_label_when_redact():
    guard = guardrail.Pii(
        custom_patterns=[
            {"name": "internal_id", "pattern": r"INT-\d{6}", "action": "redact"}
        ]
    )

    assert guard._custom_actions["internal_id"] == (
        "redact",
        REDACTED_PLACEHOLDER,
    )


# --------------------------------------------------------------------------- #
# Config validation                                                            #
# --------------------------------------------------------------------------- #


def test_pii_actions_unknown_slug_raises():
    with pytest.raises(ValueError, match="unknown slug"):
        guardrail.Pii(pii_actions={"nonexistent": "block"})


def test_pii_actions_invalid_action_raises():
    with pytest.raises(ValueError, match="must be 'redact' or 'block'"):
        guardrail.Pii(pii_actions={"ssn": "delete"})


def test_custom_pattern_missing_field_raises():
    with pytest.raises(ValueError, match="missing required field"):
        guardrail.Pii(
            custom_patterns=[
                {"name": "x", "pattern": r"\d+"}  # missing "action"
            ]
        )


def test_custom_pattern_invalid_action_raises():
    with pytest.raises(ValueError, match="must be 'redact' or 'block'"):
        guardrail.Pii(
            custom_patterns=[{"name": "x", "pattern": r"\d+", "action": "delete"}]
        )


def test_custom_pattern_redos_nested_quantifier_rejected():
    """(a+)+ is the canonical ReDoS shape. Must be rejected at config time."""
    with pytest.raises(ValueError, match="catastrophic backtracking"):
        guardrail.Pii(
            custom_patterns=[{"name": "bad", "pattern": r"(a+)+", "action": "redact"}]
        )


def test_custom_pattern_redos_alternation_rejected():
    """(a|a)* is the second canonical ReDoS shape."""
    with pytest.raises(ValueError, match="catastrophic backtracking"):
        guardrail.Pii(
            custom_patterns=[{"name": "bad", "pattern": r"(a|a)*", "action": "redact"}]
        )


def test_is_unsafe_pattern_helper_directly():
    assert _is_unsafe_pattern(r"(a+)+") is True
    assert _is_unsafe_pattern(r"(a*)*") is True
    assert _is_unsafe_pattern(r"(a+)*") is True
    assert _is_unsafe_pattern(r"(a*)+") is True
    assert _is_unsafe_pattern(r"(a|b)+") is True
    assert _is_unsafe_pattern(r"(a|b)*") is True
    # Safe patterns.
    assert _is_unsafe_pattern(r"AKIA[0-9A-Z]{16}") is False
    assert (
        _is_unsafe_pattern(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}") is False
    )
    assert _is_unsafe_pattern(r"\b\d{3}-\d{2}-\d{4}\b") is False
    assert _is_unsafe_pattern(r"\b\w+\b") is False


def test_custom_pattern_invalid_regex_raises():
    """Malformed regex fails at re.compile, not silently later."""
    with pytest.raises(Exception):  # re.error
        guardrail.Pii(
            custom_patterns=[
                {"name": "bad", "pattern": r"[unclosed", "action": "redact"}
            ]
        )


# --------------------------------------------------------------------------- #
# Built-in pattern matching                                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture
def guard():
    """A guardrail with the full prefilter enabled (redact defaults)."""
    return guardrail.Pii()


def test_email_matched(guard):
    assert guard._find_matches("Contact me at user@example.com please.")
    matches = guard._find_matches("Contact me at user@example.com please.")
    assert any(m.slug == "email" for m in matches)


def test_email_plus_tag_and_subdomain(guard):
    matches = guard._find_matches("name+tag@subdomain.example.co")
    assert any(m.slug == "email" for m in matches)


def test_phone_matched_dashed(guard):
    matches = guard._find_matches("Call 914-309-4996 for details.")
    assert any(m.slug == "phone" for m in matches)


def test_phone_matched_dotted(guard):
    matches = guard._find_matches("Call 914.309.4996 for details.")
    assert any(m.slug == "phone" for m in matches)


def test_phone_matched_no_separator(guard):
    matches = guard._find_matches("Phone: 9143094996")
    assert any(m.slug == "phone" for m in matches)


def test_phone_matched_with_country_code(guard):
    matches = guard._find_matches("Call +1 914 309 4996 now.")
    assert any(m.slug == "phone" for m in matches)


def test_ssn_matched_dashed(guard):
    matches = guard._find_matches("His SSN is 123-45-6789 by the way.")
    assert any(m.slug == "ssn" for m in matches)


def test_ssn_invalid_area_not_matched(guard):
    """000, 666, 9xx area numbers are excluded by the negative lookahead."""
    for invalid in ("000-12-3456", "666-12-3456", "900-12-3456", "999-12-3456"):
        matches = guard._find_matches(f"ssn {invalid}")
        assert not any(m.slug == "ssn" for m in matches), invalid


def test_credit_card_matched_spaced(guard):
    matches = guard._find_matches("Card: 4265 5256 0839 8752 expired.")
    assert any(m.slug == "credit-card" for m in matches)


def test_credit_card_matched_dashed(guard):
    matches = guard._find_matches("Card: 4265-5256-0839-8752 expired.")
    assert any(m.slug == "credit-card" for m in matches)


def test_credit_card_matched_no_separators(guard):
    matches = guard._find_matches("Card 4265525608398752 on file.")
    assert any(m.slug == "credit-card" for m in matches)


def test_ip_address_matched(guard):
    matches = guard._find_matches("Server at 192.168.0.1 is down.")
    assert any(m.slug == "ip-address" for m in matches)


def test_ip_address_full_range(guard):
    for ip in ("0.0.0.0", "255.255.255.255", "10.0.0.1", "127.0.0.1"):
        matches = guard._find_matches(f"host {ip}")
        assert any(m.slug == "ip-address" for m in matches), ip


def test_ip_address_octet_out_of_range_not_matched(guard):
    """256.0.0.1 must NOT match (octet > 255)."""
    matches = guard._find_matches("version 256.0.0.1 of the spec")
    assert not any(m.slug == "ip-address" for m in matches)


# --------------------------------------------------------------------------- #
# Redact action                                                                #
# --------------------------------------------------------------------------- #


def test_redact_replaces_email_with_placeholder():
    guard = guardrail.Pii(pii_actions={"email": "redact"})
    result = guard.check("Contact me at user@example.com please.")

    assert result.is_allowed is True
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("action") == "redact"
    assert "[EMAIL]" in md.get("redacted_text", "")
    assert "user@example.com" not in md.get("redacted_text", "")


def test_redact_multiple_types_in_one_input():
    guard = guardrail.Pii(pii_actions={"email": "redact", "phone": "redact"})
    text = "Email user@example.com or call 914-309-4996."
    result = guard.check(text)

    assert result.is_allowed is True
    redacted = (result.metadata or {}).get("redacted_text", "")
    assert "[EMAIL]" in redacted
    assert "[PHONE]" in redacted
    assert "user@example.com" not in redacted
    assert "914-309-4996" not in redacted


def test_redact_credit_card_takes_priority_over_phone():
    """Credit card (16 digits) takes priority over phone (10 digits) when
    patterns could overlap on the same span."""
    guard = guardrail.Pii(pii_actions={"credit-card": "redact", "phone": "redact"})
    # 16-digit number with space separators (looks like a credit card).
    text = "Charge 4265 5256 0839 8752 today."
    result = guard.check(text)

    assert result.is_allowed is True
    redacted = (result.metadata or {}).get("redacted_text", "")
    assert "[CREDIT_CARD]" in redacted
    # The 4-4-4-4 number should NOT have been re-matched as a phone.
    assert "[PHONE]" not in redacted


def test_redact_pii_detected_flag_set():
    """Even on redact, ``pii_detected=True`` so the caller can audit."""
    guard = guardrail.Pii(pii_actions={"email": "redact"})
    result = guard.check("user@example.com")

    md = result.metadata or {}
    assert md.get("pii_detected") is True
    assert "email" in md.get("pii_types", [])


# --------------------------------------------------------------------------- #
# Block action                                                                 #
# --------------------------------------------------------------------------- #


def test_block_returns_is_allowed_false():
    guard = guardrail.Pii(pii_actions={"ssn": "block"})
    result = guard.check("His SSN is 123-45-6789.")

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("action") == "block"
    assert "[SSN]" in (result.reason or "")


def test_block_does_not_include_redacted_text():
    """Blocked requests don't carry a redacted_text - they're rejected."""
    guard = guardrail.Pii(pii_actions={"ssn": "block"})
    result = guard.check("His SSN is 123-45-6789.")

    assert "redacted_text" not in (result.metadata or {})


def test_block_wins_over_redact():
    """When one preset is block and another is redact, the whole request
    is blocked (per OpenRouter: stricter action wins)."""
    guard = guardrail.Pii(pii_actions={"email": "redact", "ssn": "block"})
    result = guard.check("user@example.com, SSN 123-45-6789")

    assert result.is_allowed is False
    assert (result.metadata or {}).get("action") == "block"


# --------------------------------------------------------------------------- #
# Custom patterns                                                              #
# --------------------------------------------------------------------------- #


def test_custom_block_pattern_with_label():
    guard = guardrail.Pii(
        custom_patterns=[
            {
                "name": "aws_key",
                "pattern": r"AKIA[0-9A-Z]{16}",
                "action": "block",
                "label": "AWS Key",
            }
        ]
    )
    result = guard.check("key=AKIAIOSFODNN7EXAMPLE")

    assert result.is_allowed is False
    assert "AWS Key" in (result.reason or "")
    assert (result.metadata or {}).get("action") == "block"


def test_custom_block_pattern_without_label_uses_placeholder():
    guard = guardrail.Pii(
        custom_patterns=[
            {"name": "token", "pattern": r"TOKEN-[A-Z]{8}", "action": "block"}
        ]
    )
    result = guard.check("here is TOKEN-ABCDEFGH")

    assert result.is_allowed is False
    assert REDACTED_PLACEHOLDER in (result.reason or "")


def test_custom_redact_pattern_replaces_match():
    guard = guardrail.Pii(
        custom_patterns=[
            {
                "name": "internal_id",
                "pattern": r"INT-\d{6}",
                "action": "redact",
                "label": "[INTERNAL_ID]",
            }
        ]
    )
    result = guard.check("Order INT-123456 was placed.")

    assert result.is_allowed is True
    redacted = (result.metadata or {}).get("redacted_text", "")
    assert "[INTERNAL_ID]" in redacted
    assert "INT-123456" not in redacted


def test_custom_pattern_works_with_prefilter_disabled():
    """Custom patterns must work even when built-in prefilter is off."""
    guard = guardrail.Pii(
        enable_regex_prefilter=False,
        custom_patterns=[{"name": "x", "pattern": r"TOPSECRET\d+", "action": "block"}],
    )
    assert guard._compiled_builtins == {}
    result = guard.check("here is TOPSECRET42")

    assert result.is_allowed is False


def test_custom_patterns_combine_with_builtins():
    guard = guardrail.Pii(
        pii_actions={"email": "redact"},
        custom_patterns=[{"name": "x", "pattern": r"PROJ-\d{4}", "action": "redact"}],
    )
    result = guard.check("user@example.com and PROJ-1234")

    assert result.is_allowed is True
    redacted = (result.metadata or {}).get("redacted_text", "")
    assert "[EMAIL]" in redacted
    assert "[REDACTED]" in redacted
    assert "user@example.com" not in redacted
    assert "PROJ-1234" not in redacted


# --------------------------------------------------------------------------- #
# Prefilter disabled / opt-out                                                 #
# --------------------------------------------------------------------------- #


def test_prefilter_disabled_no_compiled_builtins():
    guard = guardrail.Pii(enable_regex_prefilter=False)
    assert guard._compiled_builtins == {}


def test_prefilter_disabled_clean_text_passes_to_dspy(guard):
    """When the prefilter is disabled, known PII must NOT be caught by the
    prefilter (it would be caught by the LLM in a real call, but we don't
    invoke the LLM here)."""
    guard = guardrail.Pii(enable_regex_prefilter=False)
    assert guard._find_matches("user@example.com") == []


# --------------------------------------------------------------------------- #
# False-positive sanity                                                        #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "benign",
    [
        "What is the capital of France?",
        "Tell me a story about a dragon and a knight.",
        "Help me write a Python function to sort a list.",
        "The meeting is at 3pm tomorrow.",
        "The package weighs 2 pounds and 10 ounces.",
        "From 100-200 BC the Roman empire expanded.",
        "Server version 1.2.3 is now available.",
    ],
)
def test_benign_prompts_not_flagged(guard, benign):
    """Benign text with no PII must produce zero prefilter matches."""
    assert guard._find_matches(benign) == [], benign


def test_email_does_not_match_in_url_path(guard):
    """``/user/admin`` must not be matched as a malformed email."""
    matches = guard._find_matches("Visit /user/admin or /api/v2.")
    assert not any(m.slug == "email" for m in matches)


# --------------------------------------------------------------------------- #
# End-to-end check()                                                           #
# --------------------------------------------------------------------------- #


def test_check_returns_guardrail_result(guard):
    result = guard.check("just a normal prompt with no PII at all")
    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "pii"


def test_check_redact_keeps_redacted_text_field_when_no_match(guard):
    """No prefilter match -> no ``redacted_text`` field is set (LLM path)."""
    result = guard.check("just a normal prompt with no PII at all")
    assert "redacted_text" not in (result.metadata or {})
