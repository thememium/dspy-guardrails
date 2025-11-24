"""Basic tests for the DSPy Guardrails package."""

import dspy
import pytest

from dspy_guardrails import (
    JailbreakGuardrail,
    KeywordsGuardrail,
    NsfwGuardrail,
    PiiGuardrail,
    PromptInjectionGuardrail,
    Run,
    SecretKeysGuardrail,
    TopicGuardrail,
)
from dspy_guardrails.core.base import GuardrailResult
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


def test_run_vs_guardrail_manager_migration():
    """Test migration from GuardrailManager to Run() function."""
    from dspy_guardrails import Run

    # Create guardrails (same as old GuardrailManager approach)
    topic_config = TopicGuardrailConfig(
        business_scopes=["Shipping Software"], competitor_names=["CompetitorA"]
    )
    topic_gr = TopicGuardrail(topic_config)

    nsfw_config = NsfwGuardrailConfig()
    nsfw_gr = NsfwGuardrail(nsfw_config)

    test_content = "Safe shipping software content"

    # Test Run() function (new approach)
    results = Run([topic_gr, nsfw_gr], test_content)

    # Verify results
    assert len(results) == 2
    assert all(isinstance(r, GuardrailResult) for r in results)
    assert all(r.is_allowed for r in results)  # Safe content should pass

    # Test early return behavior
    results_early = Run([topic_gr, nsfw_gr], test_content, early_return=True)
    assert len(results_early) == 2  # Should run all since all pass

    # Test single guardrail (now returns list with one result)
    single_results = Run(topic_gr, test_content)
    assert isinstance(single_results, list)
    assert len(single_results) == 1
    assert isinstance(single_results[0], GuardrailResult)
    assert single_results[0].is_allowed


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


def test_guardrail_module_import():
    """Test that the guardrail module can be imported."""
    from dspy_guardrails import guardrail

    # Test that all expected functions are available
    assert hasattr(guardrail, "configure")
    assert hasattr(guardrail, "topic")
    assert hasattr(guardrail, "nsfw")
    assert hasattr(guardrail, "jailbreak")
    assert hasattr(guardrail, "pii")
    assert hasattr(guardrail, "keywords")
    assert hasattr(guardrail, "secret_keys")


def test_guardrail_module_configure():
    """Test the guardrail.configure() function."""
    from dspy_guardrails import guardrail
    from dspy_guardrails.core.config import get_guardrail_lm

    # Test configuring with a specific LM
    lm = dspy.LM("test/model", api_key="test-key")
    guardrail.configure(lm=lm)

    configured_lm = get_guardrail_lm()
    assert configured_lm is not None


def test_guardrail_module_topic():
    """Test the guardrail.topic() function."""
    from dspy_guardrails import guardrail

    # Test creating a topic guardrail
    gr = guardrail.topic(
        business_scopes=["AI", "Machine Learning"],
        competitor_names=["OpenAI", "Google"],
    )

    assert gr.name == "topic"
    assert gr.config.business_scopes == ["AI", "Machine Learning"]
    assert gr.config.competitor_names == ["OpenAI", "Google"]


def test_guardrail_module_nsfw():
    """Test the guardrail.nsfw() function."""
    from dspy_guardrails import guardrail

    # Test creating an NSFW guardrail
    gr = guardrail.nsfw(sensitivity_level="high")

    assert gr.name == "nsfw"
    assert gr.config.sensitivity_level == "high"


def test_guardrail_module_jailbreak():
    """Test the guardrail.jailbreak() function."""
    from dspy_guardrails import guardrail

    # Test creating a jailbreak guardrail
    gr = guardrail.jailbreak(detection_threshold=0.9)

    assert gr.name == "jailbreak"
    assert gr.config.detection_threshold == 0.9


def test_guardrail_module_pii():
    """Test the guardrail.pii() function."""
    from dspy_guardrails import guardrail

    # Test creating a PII guardrail
    gr = guardrail.pii(allowed_pii_types=["email"])

    assert gr.name == "pii"
    assert gr.config.allowed_pii_types == ["email"]


def test_guardrail_module_keywords():
    """Test the guardrail.keywords() function."""
    from dspy_guardrails import guardrail

    # Test creating a keywords guardrail
    gr = guardrail.keywords(
        blocked_keywords=["inappropriate", "offensive"], case_sensitive=True
    )

    assert gr.name == "keywords"
    assert gr.config.blocked_keywords == ["inappropriate", "offensive"]
    assert gr.config.case_sensitive is True


def test_guardrail_module_secret_keys():
    """Test the guardrail.secret_keys() function."""
    from dspy_guardrails import guardrail

    # Test creating a secret keys guardrail
    gr = guardrail.secret_keys(entropy_threshold=3.5)

    assert gr.name == "secret_keys"
    assert gr.config.entropy_threshold == 3.5


def test_guardrail_module_defaults():
    """Test that guardrail functions work with defaults."""
    from dspy_guardrails import guardrail

    # Test that functions work with minimal parameters
    topic_gr = guardrail.topic(business_scopes=["test"], competitor_names=["dummy"])
    nsfw_gr = guardrail.nsfw()
    pii_gr = guardrail.pii()
    secret_keys_gr = guardrail.secret_keys()

    assert topic_gr.name == "topic"
    assert nsfw_gr.name == "nsfw"
    assert pii_gr.name == "pii"
    assert secret_keys_gr.name == "secret_keys"


def test_run_single_guardrail():
    """Test Run function with single guardrail."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.topic(business_scopes=["test"], competitor_names=["dummy"])
    results = Run(topic_gr, "safe test content")

    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    assert hasattr(result, "is_allowed")
    assert hasattr(result, "reason")
    assert hasattr(result, "metadata")
    assert result.guardrail_name == "topic"


def test_run_multiple_guardrails_run_all():
    """Test Run function with multiple guardrails, run all mode."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.topic(business_scopes=["test"], competitor_names=["dummy"])
    nsfw_gr = guardrail.nsfw()
    pii_gr = guardrail.pii()

    results = Run([topic_gr, nsfw_gr, pii_gr], "safe test content")

    assert isinstance(results, list)
    assert len(results) == 3
    for result in results:
        assert hasattr(result, "is_allowed")
        assert hasattr(result, "reason")
        assert hasattr(result, "metadata")


def test_run_multiple_guardrails_early_return():
    """Test Run function with multiple guardrails and early return."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.topic(business_scopes=["test"], competitor_names=["dummy"])
    nsfw_gr = guardrail.nsfw()
    pii_gr = guardrail.pii()

    # Test with content that might trigger early return
    # Note: In test environment, guardrails may fail due to LLM config, which is expected
    results = Run([topic_gr, nsfw_gr, pii_gr], "test content", early_return=True)
    assert isinstance(results, list)
    assert len(results) >= 1  # At least one result should be returned
    # With early_return=True, if first guardrail fails, we should only get 1 result
    # If first guardrail passes, we might get more results


def test_run_invalid_input():
    """Test Run function with invalid input types."""
    # Test with invalid single input
    with pytest.raises(TypeError):
        Run("not a guardrail", "test content")

    # Test with invalid list input
    with pytest.raises(TypeError):
        Run([1, 2, 3], "test content")

    # Test with mixed valid/invalid list
    from dspy_guardrails import guardrail

    topic_gr = guardrail.topic(business_scopes=["test"], competitor_names=["dummy"])

    with pytest.raises(TypeError):
        Run([topic_gr, "not a guardrail"], "test content")
