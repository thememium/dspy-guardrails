"""Tests for dspy_guardrails.core.config."""

import sys

import dspy
import pytest

from dspy_guardrails.core import config
from dspy_guardrails.core.config import (
    GibberishGuardrailConfig,
    GroundingGuardrailConfig,
    JailbreakGuardrailConfig,
    KeywordsGuardrailConfig,
    LanguageGuardrailConfig,
    NsfwGuardrailConfig,
    PromptInjectionGuardrailConfig,
    SecretKeysGuardrailConfig,
    ToneGuardrailConfig,
    TopicGuardrailConfig,
    ToxicityGuardrailConfig,
)

# --- TopicGuardrailConfig -------------------------------------------------


def test_topic_config_valid_construction():
    cfg = TopicGuardrailConfig(topic_scopes=["engineering"], blocked_topics=[])
    assert cfg.topic_scopes == ["engineering"]
    # blocked_topics may be empty; it is optional.
    assert cfg.blocked_topics == []


def test_topic_config_requires_topic_scopes():
    with pytest.raises(ValueError, match="topic_scopes is required"):
        TopicGuardrailConfig(blocked_topics=["politics"])


def test_topic_config_requires_blocked_topics():
    with pytest.raises(ValueError, match="blocked_topics is required"):
        TopicGuardrailConfig(topic_scopes=["engineering"])


def test_topic_config_rejects_empty_topic_scopes():
    with pytest.raises(ValueError, match="topic_scopes cannot be empty"):
        TopicGuardrailConfig(topic_scopes=[], blocked_topics=["politics"])


# --- NsfwGuardrailConfig --------------------------------------------------


def test_nsfw_config_valid_sensitivity_levels():
    for level in ("low", "medium", "high"):
        cfg = NsfwGuardrailConfig(sensitivity_level=level)
        assert cfg.sensitivity_level == level


def test_nsfw_config_rejects_unknown_sensitivity_level():
    with pytest.raises(
        ValueError, match="sensitivity_level must be 'low', 'medium', or 'high'"
    ):
        NsfwGuardrailConfig(sensitivity_level="extreme")


def test_nsfw_config_fills_default_content_types():
    cfg = NsfwGuardrailConfig()
    assert isinstance(cfg.nsfw_content_types, list)
    assert len(cfg.nsfw_content_types) > 0


def test_nsfw_config_keeps_explicit_content_types():
    cfg = NsfwGuardrailConfig(nsfw_content_types=["only this"])
    assert cfg.nsfw_content_types == ["only this"]


# --- JailbreakGuardrailConfig ---------------------------------------------


@pytest.mark.parametrize("threshold", [0.0, 0.8, 1.0])
def test_jailbreak_config_accepts_thresholds_in_range(threshold):
    assert (
        JailbreakGuardrailConfig(detection_threshold=threshold).detection_threshold
        == threshold
    )


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_jailbreak_config_rejects_thresholds_out_of_range(threshold):
    with pytest.raises(
        ValueError, match="detection_threshold must be between 0.0 and 1.0"
    ):
        JailbreakGuardrailConfig(detection_threshold=threshold)


# --- KeywordsGuardrailConfig ----------------------------------------------


def test_keywords_config_valid_construction():
    cfg = KeywordsGuardrailConfig(blocked_keywords=["spam"])
    assert cfg.blocked_keywords == ["spam"]


def test_keywords_config_requires_blocked_keywords():
    with pytest.raises(ValueError, match="blocked_keywords is required"):
        KeywordsGuardrailConfig()


def test_keywords_config_rejects_empty_blocked_keywords():
    with pytest.raises(ValueError, match="blocked_keywords cannot be empty"):
        KeywordsGuardrailConfig(blocked_keywords=[])


# --- SecretKeysGuardrailConfig --------------------------------------------


def test_secret_keys_config_fills_defaults():
    cfg = SecretKeysGuardrailConfig()
    assert cfg.key_patterns == []
    assert cfg.custom_patterns == []
    assert cfg.entropy_threshold == 4.0


def test_secret_keys_config_keeps_explicit_key_patterns():
    cfg = SecretKeysGuardrailConfig(key_patterns=["sk-"])
    assert cfg.key_patterns == ["sk-"]


@pytest.mark.parametrize("threshold", [0.0, 4.0])
def test_secret_keys_config_accepts_non_negative_entropy(threshold):
    assert (
        SecretKeysGuardrailConfig(entropy_threshold=threshold).entropy_threshold
        == threshold
    )


def test_secret_keys_config_rejects_negative_entropy():
    with pytest.raises(ValueError, match="entropy_threshold must be non-negative"):
        SecretKeysGuardrailConfig(entropy_threshold=-0.5)


# --- ToxicityGuardrailConfig ----------------------------------------------


@pytest.mark.parametrize("threshold", [0.0, 0.5, 1.0])
def test_toxicity_config_accepts_thresholds_in_range(threshold):
    assert (
        ToxicityGuardrailConfig(toxicity_threshold=threshold).toxicity_threshold
        == threshold
    )


@pytest.mark.parametrize("threshold", [-0.5, 1.5])
def test_toxicity_config_rejects_thresholds_out_of_range(threshold):
    with pytest.raises(
        ValueError, match="toxicity_threshold must be between 0.0 and 1.0"
    ):
        ToxicityGuardrailConfig(toxicity_threshold=threshold)


# --- GibberishGuardrailConfig ---------------------------------------------


@pytest.mark.parametrize("threshold", [0.0, 0.5, 1.0])
def test_gibberish_config_accepts_thresholds_in_range(threshold):
    assert (
        GibberishGuardrailConfig(prob_threshold=threshold).prob_threshold == threshold
    )


@pytest.mark.parametrize("threshold", [-0.5, 1.5])
def test_gibberish_config_rejects_thresholds_out_of_range(threshold):
    with pytest.raises(ValueError, match="prob_threshold must be between 0.0 and 1.0"):
        GibberishGuardrailConfig(prob_threshold=threshold)


# --- LanguageGuardrailConfig ----------------------------------------------


def test_language_config_valid_construction():
    cfg = LanguageGuardrailConfig(allowed_languages=["en", "fr"])
    assert cfg.allowed_languages == ["en", "fr"]


def test_language_config_requires_allowed_languages():
    with pytest.raises(ValueError, match="allowed_languages is required"):
        LanguageGuardrailConfig()


def test_language_config_rejects_empty_allowed_languages():
    with pytest.raises(ValueError, match="allowed_languages cannot be empty"):
        LanguageGuardrailConfig(allowed_languages=[])


# --- ToneGuardrailConfig --------------------------------------------------


def test_tone_config_fills_default_unwanted_tones():
    cfg = ToneGuardrailConfig()
    assert cfg.unwanted_tones == ["aggressive", "rude", "offensive", "sarcastic"]


def test_tone_config_keeps_explicit_unwanted_tones():
    cfg = ToneGuardrailConfig(unwanted_tones=["angry"])
    assert cfg.unwanted_tones == ["angry"]


# --- GroundingGuardrailConfig ---------------------------------------------


@pytest.mark.parametrize("threshold", [0.0, 0.7, 1.0])
def test_grounding_config_accepts_thresholds_in_range(threshold):
    assert (
        GroundingGuardrailConfig(grounding_threshold=threshold).grounding_threshold
        == threshold
    )


@pytest.mark.parametrize("threshold", [-0.5, 2.0])
def test_grounding_config_rejects_thresholds_out_of_range(threshold):
    with pytest.raises(
        ValueError, match="grounding_threshold must be between 0.0 and 1.0"
    ):
        GroundingGuardrailConfig(grounding_threshold=threshold)


# --- PromptInjectionGuardrailConfig ---------------------------------------


def test_prompt_injection_config_fills_defaults():
    cfg = PromptInjectionGuardrailConfig()
    assert cfg.injection_patterns == []
    assert cfg.custom_regex_patterns == {}


def test_prompt_injection_config_keeps_explicit_values():
    cfg = PromptInjectionGuardrailConfig(
        injection_patterns=["ignore previous"],
        custom_regex_patterns={"acme": "acme\\.corp"},
    )
    assert cfg.injection_patterns == ["ignore previous"]
    assert cfg.custom_regex_patterns == {"acme": "acme\\.corp"}


# --- configure() / get_guardrail_lm() -------------------------------------


def test_configure_stores_explicit_lm(monkeypatch):
    monkeypatch.setattr(config, "_guardrail_lm", None)
    stub_lm = object()
    config.configure(lm=stub_lm)
    assert config.get_guardrail_lm() is stub_lm


def test_configure_falls_back_to_global_dspy_lm(monkeypatch):
    monkeypatch.setattr(config, "_guardrail_lm", None)
    stub_lm = object()
    monkeypatch.setattr(dspy.settings, "lm", stub_lm)
    config.configure()
    assert config.get_guardrail_lm() is stub_lm


def test_configure_without_lm_or_global_dspy_raises(monkeypatch):
    monkeypatch.setattr(config, "_guardrail_lm", None)
    monkeypatch.setattr(dspy.settings, "lm", None)
    with pytest.raises(ValueError, match="No language model provided"):
        config.configure()


def test_configure_when_dspy_unavailable_raises(monkeypatch):
    monkeypatch.setattr(config, "_guardrail_lm", None)
    monkeypatch.setitem(sys.modules, "dspy", None)
    with pytest.raises(ValueError, match="DSPy not available"):
        config.configure()


def test_get_guardrail_lm_unconfigured_raises(monkeypatch):
    monkeypatch.setattr(config, "_guardrail_lm", None)
    with pytest.raises(ValueError, match="Guardrails not configured"):
        config.get_guardrail_lm()
