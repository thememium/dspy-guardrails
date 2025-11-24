"""Basic tests for the DSPy Guardrails package."""

from dspy_guardrails import (JailbreakGuardrail, KeywordsGuardrail,
                             NsfwGuardrail, PiiGuardrail,
                             PromptInjectionGuardrail, SecretKeysGuardrail,
                             TopicGuardrail)
from dspy_guardrails.core.config import (JailbreakGuardrailConfig,
                                         KeywordsGuardrailConfig,
                                         NsfwGuardrailConfig,
                                         PiiGuardrailConfig,
                                         PromptInjectionGuardrailConfig,
                                         SecretKeysGuardrailConfig,
                                         TopicGuardrailConfig)


def test_topic_guardrail_initialization():
    """Test that TopicGuardrail can be initialized with config."""
    config = TopicGuardrailConfig(
        business_scopes=["Shipping Software", "Logistics"],
        competitor_names=["CompetitorA", "CompetitorB"],
    )
    guardrail = TopicGuardrail(config)
    assert guardrail.name == "topic"
    assert guardrail.config.business_scopes == ["Shipping Software", "Logistics"]


def test_nsfw_guardrail_initialization():
    """Test that NsfwGuardrail can be initialized with config."""
    config = NsfwGuardrailConfig(sensitivity_level="high")
    guardrail = NsfwGuardrail(config)
    assert guardrail.name == "nsfw"
    assert guardrail.config.sensitivity_level == "high"


def test_guardrail_result_creation():
    """Test that GuardrailResult can be created."""
    from dspy_guardrails.core.base import GuardrailResult

    result = GuardrailResult(
        is_allowed=True,
        reason="Test reason",
        metadata={"test": "data"},
        guardrail_name="test",
    )
    assert result.is_allowed is True
    assert result.reason == "Test reason"
    assert result.metadata == {"test": "data"}
    assert result.guardrail_name == "test"


def test_jailbreak_guardrail_initialization():
    """Test that JailbreakGuardrail can be initialized with config."""
    config = JailbreakGuardrailConfig(detection_threshold=0.8)
    guardrail = JailbreakGuardrail(config)
    assert guardrail.name == "jailbreak"
    assert guardrail.config.detection_threshold == 0.8


def test_pii_guardrail_initialization():
    """Test that PiiGuardrail can be initialized with config."""
    config = PiiGuardrailConfig()
    guardrail = PiiGuardrail(config)
    assert guardrail.name == "pii"


def test_keywords_guardrail_initialization():
    """Test that KeywordsGuardrail can be initialized with config."""
    config = KeywordsGuardrailConfig(blocked_keywords=["bad", "word"])
    guardrail = KeywordsGuardrail(config)
    assert guardrail.name == "keywords"
    assert guardrail.config.blocked_keywords == ["bad", "word"]


def test_secret_keys_guardrail_initialization():
    """Test that SecretKeysGuardrail can be initialized with config."""
    config = SecretKeysGuardrailConfig()
    guardrail = SecretKeysGuardrail(config)
    assert guardrail.name == "secret_keys"


def test_prompt_injection_guardrail_initialization():
    """Test that PromptInjectionGuardrail can be initialized with config."""
    config = PromptInjectionGuardrailConfig()
    guardrail = PromptInjectionGuardrail(config)
    assert guardrail.name == "prompt_injection"


def test_guardrail_manager():
    """Test that GuardrailManager can orchestrate multiple guardrails."""
    from dspy_guardrails.core.manager import GuardrailManager

    manager = GuardrailManager()

    # Add guardrails
    topic_config = TopicGuardrailConfig(
        business_scopes=["Shipping Software"], competitor_names=["CompetitorA"]
    )
    manager.add_guardrail("topic", TopicGuardrail(topic_config))

    nsfw_config = NsfwGuardrailConfig()
    manager.add_guardrail("nsfw", NsfwGuardrail(nsfw_config))

    # Test manager functionality
    assert len(manager) == 2
    assert "topic" in manager
    assert "nsfw" in manager
    assert manager.list_guardrails() == ["topic", "nsfw"]

    # Test getting guardrails
    topic_guardrail = manager.get_guardrail("topic")
    assert topic_guardrail.name == "topic"

    # Test removal
    manager.remove_guardrail("topic")
    assert len(manager) == 1
    assert "topic" not in manager
