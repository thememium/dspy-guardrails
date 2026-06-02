"""Tests for the Keywords guardrail and its regex prefilter.

The prefilter is fully deterministic, so most tests can run without
invoking the DSPy LLM.  The few tests that exercise the DSPy fallback
rely on the session-scoped ``configure_guardrails`` fixture in
``conftest.py``.
"""

import pytest

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.guardrails.keywords import (
    _compile_keyword,
    _is_unsafe_pattern,
    _KeywordMatch,
)

# --------------------------------------------------------------------------- #
# Construction / config                                                        #
# --------------------------------------------------------------------------- #


def test_keywords_guardrail_type():
    guard = guardrail.Keywords(blocked_keywords=["secret"], case_sensitive=True)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "keywords"
    assert guard.config.blocked_keywords == ["secret"]
    assert guard.config.case_sensitive is True


def test_default_config_enables_prefilter():
    """Prefilter must be on by default with compiled keywords loaded."""
    guard = guardrail.Keywords(blocked_keywords=["spam"])

    assert guard.config.enable_regex_prefilter is True
    assert guard.config.word_boundary is True
    assert guard.config.use_wildcards is False
    assert len(guard._compiled_keywords) == 1
    assert guard._compiled_keywords[0][0] == "spam"


def test_prefilter_disabled_no_compiled_keywords():
    guard = guardrail.Keywords(blocked_keywords=["spam"], enable_regex_prefilter=False)
    assert guard._compiled_keywords == []


def test_multiple_keywords_all_compiled():
    guard = guardrail.Keywords(blocked_keywords=["spam", "hack", "phish"])
    assert len(guard._compiled_keywords) == 3
    compiled_kws = [kw for kw, _ in guard._compiled_keywords]
    assert compiled_kws == ["spam", "hack", "phish"]


# --------------------------------------------------------------------------- #
# _compile_keyword helper                                                      #
# --------------------------------------------------------------------------- #


def test_compile_keyword_basic():
    pat = _compile_keyword(
        "spam", word_boundary=True, use_wildcards=False, case_sensitive=False
    )
    assert pat.search("spam is bad")
    assert pat.search("SPAM IS BAD")
    assert not pat.search("spamming is annoying")


def test_compile_keyword_case_sensitive():
    pat = _compile_keyword(
        "Spam", word_boundary=True, use_wildcards=False, case_sensitive=True
    )
    assert pat.search("Spam is bad")
    assert not pat.search("spam is bad")
    assert not pat.search("SPAM IS BAD")


def test_compile_keyword_no_word_boundary():
    pat = _compile_keyword(
        "spam", word_boundary=False, use_wildcards=False, case_sensitive=False
    )
    assert pat.search("spam is bad")
    assert pat.search("spamming is annoying")


def test_compile_keyword_wildcards():
    pat = _compile_keyword(
        "fo*", word_boundary=False, use_wildcards=True, case_sensitive=False
    )
    # fo* → fo.*  (requires at least "fo" then any chars)
    assert pat.search("foo")
    assert pat.search("foobar")
    assert pat.search("fo")
    assert not pat.search("f")  # "f" alone doesn't match "fo.*"
    assert not pat.search("bar")


def test_compile_keyword_wildcard_question_mark():
    pat = _compile_keyword(
        "f?o", word_boundary=False, use_wildcards=True, case_sensitive=False
    )
    assert pat.search("foo")
    assert pat.search("fao")
    assert not pat.search("fo")


# --------------------------------------------------------------------------- #
# _is_unsafe_pattern helper                                                    #
# --------------------------------------------------------------------------- #


def test_is_unsafe_pattern_nested_quantifiers():
    assert _is_unsafe_pattern(r"(a+)+") is True
    assert _is_unsafe_pattern(r"(a*)*") is True
    assert _is_unsafe_pattern(r"(a+)*") is True
    assert _is_unsafe_pattern(r"(a*)+") is True


def test_is_unsafe_pattern_alternation():
    assert _is_unsafe_pattern(r"(a|b)+") is True
    assert _is_unsafe_pattern(r"(a|b)*") is True


def test_is_unsafe_pattern_safe_patterns():
    assert _is_unsafe_pattern(r"spam") is False
    assert _is_unsafe_pattern(r"\b\w+\b") is False
    assert _is_unsafe_pattern(r"fo.*") is False
    assert _is_unsafe_pattern(r"AKIA[0-9A-Z]{16}") is False


# --------------------------------------------------------------------------- #
# Wildcard ReDoS rejection at init                                             #
# --------------------------------------------------------------------------- #


def test_wildcard_redos_rejected_at_init():
    """Patterns with nested quantifiers must raise ValueError when use_wildcards=True."""
    # (a+)+ is the canonical ReDoS shape - but with use_wildcards, we run
    # the safety check on the *original* keyword. Since this keyword itself
    # is "(a+)+", it should be caught.
    with pytest.raises(ValueError, match="catastrophic backtracking"):
        guardrail.Keywords(blocked_keywords=["(a+)+"], use_wildcards=True)


def test_wildcard_redos_alternation_rejected():
    with pytest.raises(ValueError, match="catastrophic backtracking"):
        guardrail.Keywords(blocked_keywords=["(a|a)*"], use_wildcards=True)


def test_normal_keyword_no_redos_error():
    """Normal keywords should not trigger ReDoS rejection."""
    guard = guardrail.Keywords(blocked_keywords=["spam", "hack"], use_wildcards=True)
    assert len(guard._compiled_keywords) == 2


# --------------------------------------------------------------------------- #
# Word boundary matching                                                       #
# --------------------------------------------------------------------------- #


def test_word_boundary_matches_exact():
    """Word-boundary mode: 'spam' matches 'spam is bad'."""
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    matches = guard._find_matches("spam is bad")
    assert len(matches) == 1
    assert matches[0].keyword == "spam"
    assert matches[0].matched_text == "spam"


def test_word_boundary_rejects_substring():
    """Word-boundary mode: 'spam' does NOT match 'spamming'."""
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    matches = guard._find_matches("spamming is annoying")
    assert matches == []


def test_word_boundary_disabled_matches_substring():
    """Without word boundaries, 'spam' matches inside 'spamming'."""
    guard = guardrail.Keywords(blocked_keywords=["spam"], word_boundary=False)
    matches = guard._find_matches("spamming is annoying")
    assert len(matches) == 1
    assert matches[0].matched_text == "spam"


# --------------------------------------------------------------------------- #
# Wildcard matching                                                            #
# --------------------------------------------------------------------------- #


def test_wildcard_star_matches_prefix():
    """'fo*' → 'fo.*' is greedy, so finditer returns one match spanning from first 'foo' onward."""
    guard = guardrail.Keywords(blocked_keywords=["fo*"], use_wildcards=True)
    matches = guard._find_matches("I said foo and foobar")
    assert len(matches) >= 1
    assert all(m.keyword == "fo*" for m in matches)


def test_wildcard_question_mark_matches_single_char():
    """'f?o' matches 'foo' and 'fao' but not 'fo'."""
    guard = guardrail.Keywords(blocked_keywords=["f?o"], use_wildcards=True)
    assert len(guard._find_matches("foo")) == 1
    assert len(guard._find_matches("fao")) == 1
    assert len(guard._find_matches("fo")) == 0


def test_wildcard_case_insensitive():
    guard = guardrail.Keywords(
        blocked_keywords=["FO*"], use_wildcards=True, case_sensitive=False
    )
    matches = guard._find_matches("foo bar")
    assert len(matches) == 1


def test_wildcard_case_sensitive():
    guard = guardrail.Keywords(
        blocked_keywords=["FO*"], use_wildcards=True, case_sensitive=True
    )
    matches = guard._find_matches("foo bar")
    assert matches == []


# --------------------------------------------------------------------------- #
# Case sensitivity                                                             #
# --------------------------------------------------------------------------- #


def test_case_insensitive_default():
    guard = guardrail.Keywords(blocked_keywords=["SpAm"])
    matches = guard._find_matches("I love SPAM")
    assert len(matches) == 1


def test_case_sensitive_explicit():
    guard = guardrail.Keywords(blocked_keywords=["SpAm"], case_sensitive=True)
    matches = guard._find_matches("I love SPAM")
    assert matches == []


def test_case_sensitive_exact_match():
    guard = guardrail.Keywords(blocked_keywords=["SpAm"], case_sensitive=True)
    matches = guard._find_matches("I love SpAm")
    assert len(matches) == 1


# --------------------------------------------------------------------------- #
# _find_matches / _run_regex_prefilter                                         #
# --------------------------------------------------------------------------- #


def test_find_matches_returns_keyword_match_dataclass():
    guard = guardrail.Keywords(blocked_keywords=["hack"])
    matches = guard._find_matches("hack the system")
    assert len(matches) == 1
    assert isinstance(matches[0], _KeywordMatch)
    assert matches[0].keyword == "hack"
    assert matches[0].matched_text == "hack"


def test_find_matches_multiple_keywords():
    guard = guardrail.Keywords(blocked_keywords=["spam", "hack"])
    matches = guard._find_matches("spam and hack")
    assert len(matches) == 2
    kws = {m.keyword for m in matches}
    assert kws == {"spam", "hack"}


def test_find_matches_no_match():
    guard = guardrail.Keywords(blocked_keywords=["spam", "hack"])
    matches = guard._find_matches("hello world")
    assert matches == []


def test_find_matches_multiple_occurrences():
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    matches = guard._find_matches("spam spam spam")
    assert len(matches) == 3


def test_run_regex_prefilter_disabled_returns_empty():
    guard = guardrail.Keywords(blocked_keywords=["spam"], enable_regex_prefilter=False)
    assert guard._run_regex_prefilter("spam here") == []


def test_run_regex_prefilter_enabled_returns_matches():
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    matches = guard._run_regex_prefilter("spam here")
    assert len(matches) == 1


# --------------------------------------------------------------------------- #
# End-to-end check() — prefilter short-circuit                                 #
# --------------------------------------------------------------------------- #


def test_check_returns_guardrail_result():
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    result = guard.check("hello world no blocked words here")
    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "keywords"


def test_check_short_circuits_on_match():
    """Prefilter match -> is_allowed=False, method=regex_prefilter."""
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    result = guard.check("spam is bad")

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("contains_blocked") is True
    assert "spam" in md.get("matched_keywords", [])
    assert "Blocked keywords detected: spam" in (result.reason or "")


def test_check_short_circuit_lists_all_matched_keywords():
    guard = guardrail.Keywords(blocked_keywords=["spam", "hack", "phish"])
    result = guard.check("spam and hack are bad")

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    matched = md.get("matched_keywords", [])
    assert "spam" in matched
    assert "hack" in matched
    assert "phish" not in matched


def test_check_no_match_falls_through():
    """No prefilter match -> does NOT short-circuit (DSPy or simple fallback)."""
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    result = guard.check("hello world")
    # The result could come from DSPy or simple fallback, but not prefilter.
    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"


def test_check_metadata_includes_blocked_keywords():
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    result = guard.check("spam here")
    md = result.metadata or {}
    assert md.get("blocked_keywords") == ["spam"]
    assert md.get("case_sensitive") is False


# --------------------------------------------------------------------------- #
# Prefilter disabled                                                           #
# --------------------------------------------------------------------------- #


def test_prefilter_disabled_known_blocked_keyword_not_caught():
    """When prefilter is disabled, a known blocked keyword is NOT caught
    by the prefilter (it would be caught by the LLM in a real call,
    but we test the deterministic path here)."""
    guard = guardrail.Keywords(blocked_keywords=["spam"], enable_regex_prefilter=False)
    assert guard._find_matches("spam here") == []


def test_prefilter_disabled_no_compiled_keywords_loaded():
    guard = guardrail.Keywords(
        blocked_keywords=["spam", "hack"], enable_regex_prefilter=False
    )
    assert guard._compiled_keywords == []


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
        "I love cooking Italian food.",
        "Can you help me with my homework?",
    ],
)
def test_benign_prompts_not_flagged(benign):
    """Benign text with no blocked keywords must produce zero prefilter matches."""
    guard = guardrail.Keywords(blocked_keywords=["spam", "hack", "phish", "exploit"])
    assert guard._find_matches(benign) == [], benign


# --------------------------------------------------------------------------- #
# Word boundary edge cases                                                     #
# --------------------------------------------------------------------------- #


def test_word_boundary_at_start_of_text():
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    matches = guard._find_matches("spam is at the start")
    assert len(matches) == 1


def test_word_boundary_at_end_of_text():
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    matches = guard._find_matches("the word is spam")
    assert len(matches) == 1


def test_word_boundary_with_punctuation():
    """'spam' should match when adjacent to punctuation."""
    guard = guardrail.Keywords(blocked_keywords=["spam"])
    matches = guard._find_matches("don't say spam!")
    assert len(matches) == 1


def test_word_boundary_multi_word_keyword():
    """Multi-word keywords also get \\b wrapping."""
    guard = guardrail.Keywords(blocked_keywords=["bad word"])
    matches = guard._find_matches("that is a bad word indeed")
    assert len(matches) == 1
    assert matches[0].matched_text == "bad word"


# --------------------------------------------------------------------------- #
# Wildcard word_boundary interaction                                           #
# --------------------------------------------------------------------------- #


def test_wildcards_disables_word_boundary_even_if_set():
    """When use_wildcards=True, word_boundary is ignored (wildcards
    expand to non-word chars like '.', breaking \\b)."""
    guard = guardrail.Keywords(
        blocked_keywords=["fo*"],
        use_wildcards=True,
        word_boundary=True,  # should be ignored when wildcards are on
    )
    # 'fo*' expands to 'fo.*' which matches 'foobar' even without \b
    matches = guard._find_matches("foobar is here")
    assert len(matches) == 1
