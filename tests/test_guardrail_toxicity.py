"""Tests for the Toxicity guardrail and its conservative regex prefilter.

The prefilter is fully deterministic, so most tests can run without
invoking the DSPy LLM.  The catalog is intentionally conservative —
low recall, very high precision — catching only unambiguous, severe
cases.  Mild profanity and contextual toxicity are the LLM's job.
"""

import pytest

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.guardrails.toxicity import SEVERE_TOXICITY_PATTERNS, _ToxicityMatch

# --------------------------------------------------------------------------- #
# Construction / config                                                        #
# --------------------------------------------------------------------------- #


def test_toxicity_guardrail_type():
    guard = guardrail.Toxicity(toxicity_threshold=0.8)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "toxicity"
    assert guard.config.toxicity_threshold == 0.8


def test_toxicity_default_config_enables_prefilter():
    """Prefilter must be on by default with the full catalog loaded."""
    guard = guardrail.Toxicity()

    assert guard.config.enable_regex_prefilter is True
    assert set(guard._compiled_patterns) == set(SEVERE_TOXICITY_PATTERNS)


def test_toxicity_prefilter_disabled_no_compiled_patterns():
    guard = guardrail.Toxicity(enable_regex_prefilter=False)
    assert guard._compiled_patterns == {}


# --------------------------------------------------------------------------- #
# Each severe pattern matched (parametrized)                                   #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "slug, text",
    [
        ("explicit_threat", "i will kill you"),
        ("kill_yourself", "go die"),
        ("kill_yourself", "just kys already"),
        ("n_word_obfuscated", "you n!gger"),
        ("k_word_obfuscated", "dirty ki!e"),
        ("f_slur_obfuscated", "stop being a f@gg0t"),
        ("c_slur_obfuscated", "c h i n k"),
        ("s_slur_obfuscated", "s p i c"),
        ("sexual_violence", "rape you"),
        ("encourage_drugs", "try heroin"),
        ("doxxing", "i know your address"),
    ],
)
def test_severe_pattern_matched(slug, text):
    """Each slug in the catalog must match at least one representative example."""
    guard = guardrail.Toxicity()
    matches = guard._find_matches(text)
    assert any(m.slug == slug for m in matches), f"Expected {slug!r} in {text!r}"


# --------------------------------------------------------------------------- #
# Obfuscated variants                                                          #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text",
    [
        "n!gger",  # ! for i
        "n1gger",  # 1 for i
        "n*gger",  # * for i
        "ki!e",  # ! for i, two [i!1*] chars
        "k11e",  # 1 for both i's
        "f@gg0t",  # @ for a, 0 for o
        "f*ggot",  # * for a
        "c*!nk",  # * for h, ! for i
    ],
)
def test_obfuscated_slurs_detected(text):
    guard = guardrail.Toxicity()
    matches = guard._find_matches(text)
    assert len(matches) >= 1, f"Obfuscated slur not detected: {text!r}"


# --------------------------------------------------------------------------- #
# No false positives on mild profanity                                         #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "benign",
    [
        "this is shit",
        "damn it",
        "hell no",
        "what the hell",
        "oh crap",
        "that sucks",
        "you suck",
        "bullshit",
        "bastard",
    ],
)
def test_mild_profanity_not_flagged(benign):
    """Mild profanity must NOT trigger the prefilter — the LLM handles it."""
    guard = guardrail.Toxicity()
    assert guard._find_matches(benign) == [], benign


# --------------------------------------------------------------------------- #
# No false positives on news / educational text                                #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "benign",
    [
        "The war caused many casualties.",
        "Victims of assault deserve justice.",
        "The documentary covers the history of racial slurs in America.",
        "She studies the etymology of offensive words.",
        "The court heard testimony about the defendant's threats.",
        "Law enforcement addressed the doxxing incident.",
        "The pharmacist discussed drug abuse prevention.",
        "He will help you with your homework.",
        "I will kill the process running on port 8080.",
    ],
)
def test_news_educational_text_not_flagged(benign):
    """News / educational text with no severe toxicity must produce zero matches."""
    guard = guardrail.Toxicity()
    assert guard._find_matches(benign) == [], benign


# --------------------------------------------------------------------------- #
# End-to-end check() short-circuit                                             #
# --------------------------------------------------------------------------- #


def test_check_short_circuits_on_match():
    """Severe toxicity short-circuits with is_allowed=False, method=regex_prefilter."""
    guard = guardrail.Toxicity()
    result = guard.check("i will kill you")

    assert result.is_allowed is False
    assert result.guardrail_name == "toxicity"
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("is_toxic") is True
    assert md.get("toxicity_score") == 1.0
    assert "explicit_threat" in md.get("toxicity_types", [])
    assert "explicit_threat" in (result.reason or "")


def test_check_metadata_contains_matched_patterns():
    guard = guardrail.Toxicity()
    result = guard.check("go die now")

    md = result.metadata or {}
    matched = md.get("matched_patterns", [])
    assert len(matched) >= 1
    assert any(p["slug"] == "kill_yourself" for p in matched)
    assert matched[0]["matched_text"]  # non-empty


def test_check_metadata_contains_threshold():
    guard = guardrail.Toxicity(toxicity_threshold=0.7)
    result = guard.check("kys")

    md = result.metadata or {}
    assert md.get("threshold") == 0.7


def test_check_no_match_falls_through_to_dspy(guard=None):
    """Clean text produces no prefilter match (LLM path, but we don't invoke it)."""
    guard = guardrail.Toxicity()
    # Verify prefilter produces no matches for benign input.
    matches = guard._find_matches("What is the capital of France?")
    assert matches == []


def test_check_returns_guardrail_result_on_benign():
    guard = guardrail.Toxicity()
    result = guard.check("just a normal prompt")
    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "toxicity"


# --------------------------------------------------------------------------- #
# Prefilter disabled — severe content is NOT caught by prefilter                #
# --------------------------------------------------------------------------- #


def test_prefilter_disabled_severe_content_not_caught():
    """When prefilter is disabled, even severe content must NOT be caught
    by the prefilter (it would be caught by the LLM in a real call)."""
    guard = guardrail.Toxicity(enable_regex_prefilter=False)
    assert guard._find_matches("i will kill you") == []
    assert guard._find_matches("go die") == []
    assert guard._find_matches("n!gger") == []


def test_prefilter_disabled_check_returns_guardrail_result():
    guard = guardrail.Toxicity(enable_regex_prefilter=False)
    result = guard.check("just a normal prompt")
    assert isinstance(result, GuardrailResult)


# --------------------------------------------------------------------------- #
# _ToxicityMatch dataclass                                                    #
# --------------------------------------------------------------------------- #


def test_toxicity_match_dataclass():
    m = _ToxicityMatch(slug="kill_yourself", matched_text="kys")
    assert m.slug == "kill_yourself"
    assert m.matched_text == "kys"


# --------------------------------------------------------------------------- #
# Multiple matches in one input                                                #
# --------------------------------------------------------------------------- #


def test_multiple_severe_patterns_in_one_input():
    guard = guardrail.Toxicity()
    result = guard.check("n!gger i will kill you")

    assert result.is_allowed is False
    md = result.metadata or {}
    types = md.get("toxicity_types", [])
    assert "n_word_obfuscated" in types
    assert "explicit_threat" in types
