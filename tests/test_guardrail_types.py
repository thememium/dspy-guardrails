import dspy
import pytest

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


@pytest.fixture(scope="session", autouse=True)
def configure_guardrails_for_types():
    from dspy_guardrails import configure

    lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025")
    configure(lm=lm)


def test_topic_guardrail_type():
    guard = guardrail.Topic(
        topic_scopes=["AI", "Machine Learning"],
        blocked_topics=["spam"],
    )

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "topic"
    assert guard.config.topic_scopes == ["AI", "Machine Learning"]
    assert guard.config.blocked_topics == ["spam"]


def test_nsfw_guardrail_type():
    guard = guardrail.Nsfw(sensitivity_level="high")

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "nsfw"
    assert guard.config.sensitivity_level == "high"
    assert guard.config.nsfw_content_types


def test_pii_guardrail_type():
    guard = guardrail.Pii(allowed_pii_types=["email"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "pii"
    assert guard.config.allowed_pii_types == ["email"]


def test_toxicity_guardrail_type():
    guard = guardrail.Toxicity(toxicity_threshold=0.8)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "toxicity"
    assert guard.config.toxicity_threshold == 0.8


def test_tone_guardrail_type():
    guard = guardrail.Tone(desired_tone="helpful", unwanted_tones=["sarcastic"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "tone"
    assert guard.config.desired_tone == "helpful"
    assert guard.config.unwanted_tones == ["sarcastic"]


def test_grounding_guardrail_type():
    guard = guardrail.Grounding(grounding_threshold=0.9)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "grounding"
    assert guard.config.grounding_threshold == 0.9


def test_language_guardrail_type():
    guard = guardrail.Language(allowed_languages=["en", "es"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "language"
    assert guard.config.allowed_languages == ["en", "es"]


def test_keywords_guardrail_type():
    guard = guardrail.Keywords(blocked_keywords=["secret"], case_sensitive=True)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "keywords"
    assert guard.config.blocked_keywords == ["secret"]
    assert guard.config.case_sensitive is True


def test_secret_keys_guardrail_type():
    guard = guardrail.SecretKeys(key_patterns=["sk-"], entropy_threshold=3.5)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "secret_keys"
    assert guard.config.key_patterns == ["sk-"]
    assert guard.config.entropy_threshold == 3.5


def test_gibberish_guardrail_type():
    guard = guardrail.Gibberish(prob_threshold=0.7)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "gibberish"
    assert guard.config.prob_threshold == 0.7


def test_prompt_injection_guardrail_type():
    guard = guardrail.PromptInjection(injection_patterns=["ignore previous"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "prompt_injection"
    assert guard.config.injection_patterns == ["ignore previous"]


def test_jailbreak_guardrail_type():
    guard = guardrail.Jailbreak(detection_threshold=0.9)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "jailbreak"
    assert guard.config.detection_threshold == 0.9
