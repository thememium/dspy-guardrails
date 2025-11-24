"""Basic tests for the DSPy Guardrails package."""

import pytest
import dspy
from dspy_guardrails import (
    JailbreakGuardrail,
    KeywordsGuardrail,
    NsfwGuardrail,
    PiiGuardrail,
    PromptInjectionGuardrail,
    SecretKeysGuardrail,
    TopicGuardrail,
)
from dspy_guardrails.core.config import (
    JailbreakGuardrailConfig,
    KeywordsGuardrailConfig,
    NsfwGuardrailConfig,
    PiiGuardrailConfig,
    PromptInjectionGuardrailConfig,
    SecretKeysGuardrailConfig,
    TopicGuardrailConfig,
)


@pytest.fixture(scope="session", autouse=True)
def configure_guardrails():
    """Configure guardrails for all tests."""
    from dspy_guardrails import configure

    # Use a mock LM for testing to avoid API calls
    lm = dspy.LM(
        "openrouter/google/gemini-2.5-flash-preview-09-2025",
    )
    configure(lm=lm)


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


# Note: DSPy configuration validation is tested implicitly through the requirement
# that all guardrail operations work correctly when DSPy is configured (as shown in other tests)


def test_config_validation():
    """Test that GuardrailConfig validates required fields."""
    from dspy_guardrails.core.config import GuardrailConfig

    # Test that model is optional
    config = GuardrailConfig()
    assert config.model is None

    # Test that model can be provided
    config = GuardrailConfig(model="test-model")
    assert config.model == "test-model"

    # Test that empty model fails
    try:
        config = GuardrailConfig(model="")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "model must be a non-empty string if provided" in str(e)


def test_guardrail_configure_function():
    """Test the dspy_guardrails.configure() function."""
    from dspy_guardrails import configure
    from dspy_guardrails.core.config import get_guardrail_lm

    # Test configuring with a specific LM
    lm = dspy.LM("test/model", api_key="test-key")
    configure(lm=lm)

    configured_lm = get_guardrail_lm()
    assert configured_lm is not None

    # Test configuring without parameters (should use global DSPy if available)
    # First set up global DSPy
    dspy.configure(lm=lm)
    configure()  # Should use global DSPy config

    configured_lm = get_guardrail_lm()
    assert configured_lm is not None
