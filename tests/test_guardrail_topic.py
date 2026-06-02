"""Tests for the Topic guardrail blocked-topic regex prefilter.

The prefilter is fully deterministic — it checks ``blocked_topics``
as case-insensitive substrings before the DSPy LLM call.  Tests that
exercise ``check()`` on blocked text never invoke the LLM because the
prefilter short-circuits first.  Tests that verify LLM fallback
behavior use ``_find_matches()`` directly to avoid flaky LLM calls.
"""

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.guardrails.topic import _is_unsafe_pattern

# --------------------------------------------------------------------------- #
# Construction / compiled blocked topics                                       #
# --------------------------------------------------------------------------- #


def test_topic_guardrail_type():
    guard = guardrail.Topic(
        topic_scopes=["AI", "Machine Learning"],
        blocked_topics=["spam"],
    )

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "topic"
    assert guard.config.topic_scopes == ["AI", "Machine Learning"]
    assert guard.config.blocked_topics == ["spam"]


def test_default_config_compiles_blocked_topics():
    """Prefilter must be on by default with blocked_topics compiled."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam", "casino"],
    )

    assert guard.config.enable_blocked_topic_prefilter is True
    assert len(guard._compiled_blocked) == 2
    compiled_topics = [t for t, _ in guard._compiled_blocked]
    assert "spam" in compiled_topics
    assert "casino" in compiled_topics


def test_prefilter_disabled_no_compiled_blocked():
    """When prefilter is disabled, _compiled_blocked must be empty."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
        enable_blocked_topic_prefilter=False,
    )

    assert guard._compiled_blocked == []


def test_empty_blocked_topics_compiles_empty_list():
    """Empty blocked_topics yields an empty compiled list (prefilter fires but finds nothing)."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=[],
    )

    assert guard._compiled_blocked == []


# --------------------------------------------------------------------------- #
# _is_unsafe_pattern (copy from pii — verify it works)                         #
# --------------------------------------------------------------------------- #


def test_is_unsafe_pattern_rejects_nested_quantifiers():
    assert _is_unsafe_pattern(r"(a+)+") is True
    assert _is_unsafe_pattern(r"(a*)*") is True
    assert _is_unsafe_pattern(r"(a+)*") is True
    assert _is_unsafe_pattern(r"(a*)+") is True


def test_is_unsafe_pattern_rejects_alternation_quantifiers():
    assert _is_unsafe_pattern(r"(a|b)+") is True
    assert _is_unsafe_pattern(r"(a|b)*") is True


def test_is_unsafe_pattern_allows_safe_patterns():
    assert _is_unsafe_pattern(r"hello world") is False
    assert _is_unsafe_pattern(r"\b\d+\b") is False
    assert _is_unsafe_pattern(r"openai") is False


# --------------------------------------------------------------------------- #
# Substring matching — _find_matches                                            #
# --------------------------------------------------------------------------- #


def test_substring_match_simple():
    """blocked_topics=["spam"] matches "buy our spam service"."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
    )
    matches = guard._find_matches("buy our spam service")
    assert len(matches) == 1
    assert matches[0].topic == "spam"
    assert matches[0].matched_text == "spam"


def test_substring_match_case_insensitive():
    """blocked_topics=["SPAM"] matches "spam service" (lowercase input)."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["SPAM"],
    )
    matches = guard._find_matches("buy our spam service")
    assert len(matches) == 1
    assert matches[0].topic == "SPAM"
    assert matches[0].matched_text == "spam"


def test_substring_match_case_insensitive_uppercase_input():
    """blocked_topics=["spam"] matches "SPAM service" (uppercase input)."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
    )
    matches = guard._find_matches("buy our SPAM service")
    assert len(matches) == 1
    assert matches[0].matched_text == "SPAM"


def test_multiword_match():
    """blocked_topics=["open ai"] matches "we use Open AI in production"."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["open ai"],
    )
    matches = guard._find_matches("we use Open AI in production")
    assert len(matches) == 1
    assert matches[0].topic == "open ai"
    assert matches[0].matched_text == "Open AI"


def test_multiple_blocked_topics_match():
    """Multiple blocked topics can be detected in one input."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam", "casino"],
    )
    matches = guard._find_matches("spam and casino offers here")
    assert len(matches) == 2
    matched_topics = {m.topic for m in matches}
    assert matched_topics == {"spam", "casino"}


def test_repeated_occurrences():
    """Same blocked topic appearing twice yields two matches."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
    )
    matches = guard._find_matches("spam is bad, don't do spam")
    assert len(matches) == 2


# --------------------------------------------------------------------------- #
# No false positives on benign text                                            #
# --------------------------------------------------------------------------- #


def test_no_false_positive_on_benign_text():
    """Benign text that doesn't mention blocked topics produces zero matches."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam", "casino"],
    )
    benign_texts = [
        "I want to learn about neural networks",
        "Explain gradient descent to me",
        "What is the weather today?",
        "Help me write a Python function",
        "The meeting is at 3pm tomorrow",
    ]
    for text in benign_texts:
        assert guard._find_matches(text) == [], f"False positive on: {text}"


def test_no_false_positive_substring_not_present():
    """Blocked topic substring must actually appear in the text."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
    )
    assert guard._find_matches("I love cooking with eggs and ham") == []


# --------------------------------------------------------------------------- #
# End-to-end check() short-circuit                                             #
# --------------------------------------------------------------------------- #


def test_check_short_circuits_on_blocked_topic():
    """check() returns is_allowed=False with method=regex_prefilter on match."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
    )
    result = guard.check("buy our spam service")

    assert isinstance(result, GuardrailResult)
    assert result.is_allowed is False
    assert result.guardrail_name == "topic"
    assert "spam" in (result.reason or "").lower()

    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("is_on_topic") is False
    assert "spam" in md.get("matched_blocked_topics", [])
    assert md.get("topic_scopes") == ["AI"]
    assert md.get("blocked_topics") == ["spam"]
    assert len(md.get("off_topic_reasons", [])) > 0


def test_check_short_circuit_reason_lists_all_matched_topics():
    """Reason includes all matched blocked topics."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam", "casino"],
    )
    result = guard.check("spam and casino deals here")

    assert result.is_allowed is False
    reason = result.reason or ""
    assert "spam" in reason.lower()
    assert "casino" in reason.lower()

    md = result.metadata or {}
    matched = md.get("matched_blocked_topics", [])
    assert "spam" in matched
    assert "casino" in matched


def test_check_short_circuit_metadata_has_off_topic_reasons():
    """metadata['off_topic_reasons'] contains per-match reason strings."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
    )
    result = guard.check("buy our spam service")

    md = result.metadata or {}
    reasons = md.get("off_topic_reasons", [])
    assert len(reasons) >= 1
    assert any("spam" in r.lower() for r in reasons)


def test_check_guardrail_result_type():
    """check() always returns a GuardrailResult."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
    )
    result = guard.check("spam content")
    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "topic"


# --------------------------------------------------------------------------- #
# Prefilter disabled — blocked topic NOT caught by prefilter                   #
# --------------------------------------------------------------------------- #


def test_prefilter_disabled_blocked_topic_not_caught():
    """When prefilter is disabled, blocked topics are NOT caught by the
    prefilter (they would be caught by the LLM in production)."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
        enable_blocked_topic_prefilter=False,
    )
    # _find_matches should return nothing (no compiled patterns).
    assert guard._find_matches("buy our spam service") == []


def test_prefilter_disabled_check_returns_guardrail_result():
    """With prefilter disabled, check() still returns a GuardrailResult
    (falls through to DSPy — we just verify it doesn't crash)."""
    guard = guardrail.Topic(
        topic_scopes=["AI"],
        blocked_topics=["spam"],
        enable_blocked_topic_prefilter=False,
    )
    result = guard.check("tell me about AI")
    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "topic"


# --------------------------------------------------------------------------- #
# topic_scopes NOT evaluated by prefilter                                      #
# --------------------------------------------------------------------------- #


def test_prefilter_does_not_evaluate_topic_scopes():
    """The prefilter ONLY checks blocked_topics.  On-topic text that
    does not mention any blocked topic must produce zero prefilter
    matches — the prefilter does not judge whether the text is on-topic."""
    guard = guardrail.Topic(
        topic_scopes=["AI", "Machine Learning"],
        blocked_topics=["spam"],
    )
    # This text is on-topic (about AI) and has no blocked topics.
    matches = guard._find_matches("Tell me about deep learning and neural nets")
    assert matches == []


def test_prefilter_ignores_off_topic_text_without_blocked_topics():
    """Off-topic text that does NOT mention blocked topics is NOT caught
    by the prefilter — that's the LLM's job via topic_scopes."""
    guard = guardrail.Topic(
        topic_scopes=["AI", "Machine Learning"],
        blocked_topics=["spam"],
    )
    # This text is off-topic (cooking) but has no blocked topics.
    matches = guard._find_matches("How do I bake a chocolate cake?")
    assert matches == []


def test_prefilter_only_checks_blocked_topics_not_scopes():
    """Even if a topic_scopes entry appears in text, the prefilter doesn't
    care — it only looks for blocked_topics substrings."""
    guard = guardrail.Topic(
        topic_scopes=["AI", "Machine Learning"],
        blocked_topics=["casino"],
    )
    # "AI" is a topic_scope but not a blocked_topic — no match.
    matches = guard._find_matches("I love AI and machine learning")
    assert matches == []

    # "casino" IS a blocked_topic — match.
    matches = guard._find_matches("Check out this casino game")
    assert len(matches) == 1
    assert matches[0].topic == "casino"


# --------------------------------------------------------------------------- #
# _is_unsafe_pattern not used for simple escaped substrings                    #
# --------------------------------------------------------------------------- #


def test_escaped_blocked_topics_are_safe_patterns():
    """re.escape on plain words never creates ReDoS-prone patterns."""
    import re

    for topic in ["spam", "casino", "open ai", "buy now", "free money"]:
        escaped = re.escape(topic)
        assert _is_unsafe_pattern(escaped) is False, f"False alarm on: {topic}"
