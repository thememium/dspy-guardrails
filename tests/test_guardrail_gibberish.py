"""Tests for the Gibberish guardrail and its regex prefilter.

The prefilter is fully deterministic, so all tests run without invoking
the DSPy LLM. Mirrors the structure of ``tests/test_guardrail_pii.py``.
"""

import pytest

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.guardrails.gibberish import (
    GIBBERISH_SIGNALS,
    _GibberishSignal,
    _has_no_whitespace,
    _is_unsafe_pattern,
    _vowel_ratio,
)

# --------------------------------------------------------------------------- #
# Construction / config                                                        #
# --------------------------------------------------------------------------- #


def test_gibberish_guardrail_type():
    guard = guardrail.Gibberish(prob_threshold=0.7)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "gibberish"
    assert guard.config.prob_threshold == 0.7


def test_default_config_enables_prefilter():
    """Prefilter must be on by default with all signal patterns compiled."""
    guard = guardrail.Gibberish()

    assert guard.config.enable_regex_prefilter is True
    assert len(guard._compiled_signals) == len(GIBBERISH_SIGNALS)


def test_prefilter_disabled_no_compiled_signals():
    guard = guardrail.Gibberish(enable_regex_prefilter=False)
    assert guard._compiled_signals == []


# --------------------------------------------------------------------------- #
# Structural helper tests                                                      #
# --------------------------------------------------------------------------- #


def test_vowel_ratio_normal_english():
    """Normal English text should have a healthy vowel ratio."""
    ratio = _vowel_ratio("the quick brown fox jumps over the lazy dog")
    assert ratio > 0.25


def test_vowel_ratio_all_consonants():
    ratio = _vowel_ratio("bcdfghjklmnpqrstvwxyz")
    assert ratio == 0.0


def test_vowel_ratio_all_vowels():
    ratio = _vowel_ratio("aeiouaeiou")
    assert ratio == 1.0


def test_vowel_ratio_empty_string():
    assert _vowel_ratio("") == 0.0


def test_vowel_ratio_no_letters():
    assert _vowel_ratio("12345 !@#") == 0.0


def test_has_no_whitespace_long_no_spaces():
    assert _has_no_whitespace("abcdefghijklmnop" * 3) is True


def test_has_no_whitespace_with_spaces():
    assert _has_no_whitespace("hello world this is a test string ok") is False


def test_has_no_whitespace_short():
    assert _has_no_whitespace("abcdefgh") is False


def test_has_no_whitespace_custom_min_length():
    assert _has_no_whitespace("abcde", min_length=5) is True
    assert _has_no_whitespace("abcd", min_length=5) is False


# --------------------------------------------------------------------------- #
# _is_unsafe_pattern (ReDoS check)                                             #
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
    assert _is_unsafe_pattern(r"[bcdfghjklmnpqrstvwxyz]{8,}") is False
    assert _is_unsafe_pattern(r"(.)\1{5,}") is False
    assert _is_unsafe_pattern(r"[qwertyuiop]{5,}") is False


# --------------------------------------------------------------------------- #
# Signal slug matching (parametrized)                                          #
# --------------------------------------------------------------------------- #


@pytest.fixture
def guard():
    """A guardrail with the full prefilter enabled."""
    return guardrail.Gibberish()


@pytest.mark.parametrize(
    "text,expected_slug",
    [
        ("bcdfghjklmnpqrst", "all_consonants"),
        ("hythmstrngthngth", "all_consonants"),
        ("qwertyuiop", "qwerty_row"),
        ("qwertyuiopasdf", "qwerty_row"),
        ("asdfghjkl", "asdf_row"),
        ("asdfghjklaaa", "asdf_row"),
        ("zxcvbnm", "zxcv_row"),
        ("zxcvbnmzzz", "zxcv_row"),
        ("aaaaaaaa", "single_char_repeat"),
        ("00000000", "single_char_repeat"),
        (".........", "punctuation_spam"),
        ("?????????", "punctuation_spam"),
        ("!!!!!", "punctuation_spam"),
    ],
)
def test_signal_slug_matched(guard, text, expected_slug):
    signals = guard._find_signals(text)
    slugs = [s.slug for s in signals]
    assert expected_slug in slugs, (
        f"Expected {expected_slug} in signals for {text!r}, got {slugs}"
    )


# --------------------------------------------------------------------------- #
# _find_signals details                                                        #
# --------------------------------------------------------------------------- #


def test_find_signals_returns_gibberish_signal_instances(guard):
    signals = guard._find_signals("qwertyuiop")
    assert len(signals) >= 1
    assert all(isinstance(s, _GibberishSignal) for s in signals)
    assert signals[0].slug == "qwerty_row"
    assert signals[0].matched_text == "qwertyuiop"


def test_find_signals_multiple_matches(guard):
    """A string with keyboard mash AND all-consonant run should produce
    multiple signals."""
    # "qwerty" has no vowels (except y, but our vowel set is aeiou)
    signals = guard._find_signals("qwertyuiop")
    slugs = [s.slug for s in signals]
    # qwertyuiop matches qwerty_row; the full string also has long
    # consonant-ish runs
    assert "qwerty_row" in slugs


def test_find_signals_clean_text(guard):
    signals = guard._find_signals("The quick brown fox jumps over the lazy dog.")
    assert signals == []


# --------------------------------------------------------------------------- #
# _score()                                                                     #
# --------------------------------------------------------------------------- #


def test_score_capped_at_one(guard):
    """Even with many signals the score must not exceed 1.0."""
    signals = [
        _GibberishSignal(slug="a", matched_text="x", score=0.7),
        _GibberishSignal(slug="b", matched_text="y", score=0.6),
        _GibberishSignal(slug="c", matched_text="z", score=0.6),
    ]
    score = guard._score(signals, "some long text without spaces here ok")
    assert score <= 1.0


def test_score_empty_signals(guard):
    assert guard._score([], "Hello, this is a perfectly normal sentence.") == 0.0


def test_score_sums_signal_weights(guard):
    signals = [
        _GibberishSignal(slug="a", matched_text="x", score=0.3),
        _GibberishSignal(slug="b", matched_text="y", score=0.2),
    ]
    # Normal text with spaces — no structural bonuses.
    score = guard._score(signals, "This is a normal sentence with spaces.")
    assert score == pytest.approx(0.5)


def test_score_structural_vowel_ratio_bonus(guard):
    """Long text with very few vowels gets a +0.5 structural bonus."""
    # 30+ chars, no vowels, no spaces → vowel_ratio=0.0 + no_whitespace
    text = "bcdfghjklmnpqrstvwxyzbcdfghjklm"
    signals = guard._find_signals(text)
    score = guard._score(signals, text)
    # all_consonants signal (0.7) + vowel_ratio bonus (0.5) + no_whitespace (0.4) = 1.6, capped at 1.0
    assert score == 1.0


def test_score_structural_no_whitespace_bonus(guard):
    """Long string with no spaces gets a +0.4 structural bonus."""
    # 30+ chars with spaces → no no_whitespace bonus
    text_with_spaces = "The quick brown fox jumps over lazy dog"
    # 30+ chars without spaces → +0.4
    text_no_spaces = "Thisisasentencebutwithnospacesat"
    score_ws = guard._score([], text_with_spaces)
    score_no_ws = guard._score([], text_no_spaces)
    assert score_ws == 0.0
    assert score_no_ws == pytest.approx(0.4)


# --------------------------------------------------------------------------- #
# _run_regex_prefilter()                                                       #
# --------------------------------------------------------------------------- #


def test_prefilter_short_text_returns_zero(guard):
    """Text < 10 chars is too short to judge → score 0.0."""
    score, signals = guard._run_regex_prefilter("hello")
    assert score == 0.0
    assert signals == []


def test_prefilter_short_text_exact_boundary(guard):
    """9 chars is still too short; 10 chars is evaluated."""
    score_9, _ = guard._run_regex_prefilter("a" * 9)
    assert score_9 == 0.0

    # 10 repeated chars → single_char_repeat signal fires
    score_10, signals = guard._run_regex_prefilter("a" * 10)
    assert score_10 > 0.0
    assert any(s.slug == "single_char_repeat" for s in signals)


def test_prefilter_keyboard_mash(guard):
    score, signals = guard._run_regex_prefilter("qwertyuiopasdfghjkl")
    assert score > 0.0
    slugs = [s.slug for s in signals]
    assert "qwerty_row" in slugs or "asdf_row" in slugs


def test_prefilter_all_consonants_long(guard):
    # 30+ consonants: signal + vowel_ratio + no_whitespace bonuses
    text = "bcdfghjklmnpqrstvwxyzbcdfghjklm"
    score, signals = guard._run_regex_prefilter(text)
    assert score >= 0.7
    assert any(s.slug == "all_consonants" for s in signals)


def test_prefilter_single_char_repeat(guard):
    score, signals = guard._run_regex_prefilter("aaaaaaaabbbb")
    assert score > 0.0
    assert any(s.slug == "single_char_repeat" for s in signals)


def test_prefilter_punctuation_spam(guard):
    score, signals = guard._run_regex_prefilter("What is this?????????")
    assert score > 0.0
    assert any(s.slug == "punctuation_spam" for s in signals)


def test_prefilter_normal_english_low_score(guard):
    score, signals = guard._run_regex_prefilter(
        "Can you help me write a Python function to sort a list?"
    )
    assert score < 0.5


# --------------------------------------------------------------------------- #
# End-to-end check() short-circuit                                             #
# --------------------------------------------------------------------------- #


def test_check_short_circuits_on_keyboard_mash(guard):
    result = guard.check("qwertyuiopasdfghjklzxcvbnm")
    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("is_gibberish") is True
    assert md.get("gibberish_probability", 0) >= guard.config.prob_threshold


def test_check_short_circuits_on_all_consonants_long(guard):
    result = guard.check("bcdfghjklmnpqrstvwxyzbcdfghjklm")
    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"


def test_check_short_circuits_on_single_char_repeat(guard):
    result = guard.check("aaaaaaaaaaaaaaaa")
    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert "single_char_repeat" in [s["slug"] for s in md.get("signals", [])]


def test_check_short_circuits_on_punctuation_spam(guard):
    result = guard.check("What does this mean?????????????")
    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert "punctuation_spam" in [s["slug"] for s in md.get("signals", [])]


def test_check_reason_contains_score(guard):
    result = guard.check("qwertyuiopasdfghjkl")
    assert result.is_allowed is False
    assert "score:" in (result.reason or "").lower()


def test_check_metadata_has_signals_list(guard):
    result = guard.check("qwertyuiopasdfghjkl")
    md = result.metadata or {}
    signals = md.get("signals", [])
    assert isinstance(signals, list)
    assert len(signals) >= 1
    assert "slug" in signals[0]
    assert "matched_text" in signals[0]
    assert "score" in signals[0]


# --------------------------------------------------------------------------- #
# Short text (< 10 chars) always passes                                        #
# --------------------------------------------------------------------------- #


def test_short_text_always_passes_prefilter(guard):
    for text in ["hi", "abc", "12345", "!!!!!!", "aaaaaa"]:
        score, signals = guard._run_regex_prefilter(text)
        assert score == 0.0, f"Short text {text!r} should score 0.0"
        assert signals == []


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
        "I love programming in Python and JavaScript.",
        "Can you explain how neural networks work?",
        "The quick brown fox jumps over the lazy dog.",
        "Please summarize the following article for me.",
        "How do I configure a Docker container?",
    ],
)
def test_benign_prompts_low_score(guard, benign):
    """Benign text must have a prefilter score well below threshold."""
    score, _ = guard._run_regex_prefilter(benign)
    assert score < 0.5, f"Benign text scored {score:.2f}: {benign!r}"


# --------------------------------------------------------------------------- #
# Prefilter disabled                                                           #
# --------------------------------------------------------------------------- #


def test_prefilter_disabled_clean_text_returns_no_signals():
    guard = guardrail.Gibberish(enable_regex_prefilter=False)
    assert guard._find_signals("qwertyuiopasdfghjkl") == []


# --------------------------------------------------------------------------- #
# End-to-end check() returns GuardrailResult                                   #
# --------------------------------------------------------------------------- #


def test_check_returns_guardrail_result(guard):
    result = guard.check("just a normal prompt")
    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "gibberish"


# --------------------------------------------------------------------------- #
# Custom threshold behavior                                                    #
# --------------------------------------------------------------------------- #


def test_high_threshold_lets_more_through():
    """A high threshold means more borderline text passes."""
    guard = guardrail.Gibberish(prob_threshold=0.9)
    # Punctuation spam alone has weight 0.3 — below 0.9
    score, _ = guard._run_regex_prefilter("What is this?????????")
    # Score should be below 0.9 (punctuation_spam 0.3, text has spaces so no structural bonuses)
    assert score < 0.9


def test_low_threshold_catches_more():
    """A low threshold is more aggressive."""
    guard = guardrail.Gibberish(prob_threshold=0.2)
    score, signals = guard._run_regex_prefilter("What is this?????????")
    # Punctuation spam (0.3) exceeds threshold (0.2)
    assert score >= 0.2
