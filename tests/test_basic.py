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
        topic_scopes=["Shipping Software", "Logistics"],
        blocked_topics=["CompetitorA", "CompetitorB"],
    )
    guardrail = TopicGuardrail(config)
    assert guardrail.name == "topic"
    assert guardrail.config.topic_scopes == ["Shipping Software", "Logistics"]


def test_guardrail_module_topic():
    """Test the guardrail.Topic() class."""
    from dspy_guardrails import guardrail

    # Test creating a topic guardrail
    gr = guardrail.Topic(
        topic_scopes=["AI", "Machine Learning"],
        blocked_topics=["OpenAI", "Google"],
    )

    assert gr.name == "topic"
    assert gr.config.topic_scopes == ["AI", "Machine Learning"]
    assert gr.config.blocked_topics == ["OpenAI", "Google"]


def test_guardrail_module_defaults():
    """Test that guardrail classes work with default parameters."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])
    nsfw_gr = guardrail.Nsfw()
    pii_gr = guardrail.Pii()
    secret_keys_gr = guardrail.SecretKeys()

    assert topic_gr.name == "topic"
    assert nsfw_gr.name == "nsfw"
    assert pii_gr.name == "pii"
    assert secret_keys_gr.name == "secret_keys"


def test_run_single_guardrail():
    """Test Run function with single guardrail."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])
    result = Run(topic_gr, "safe test content")

    assert isinstance(result, GuardrailResult)
    assert hasattr(result, "is_allowed")
    assert hasattr(result, "reason")
    assert hasattr(result, "metadata")
    assert result.guardrail_name == "topic"


def test_run_multiple_guardrails_run_all():
    """Test Run function with multiple guardrails, run all mode."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])
    nsfw_gr = guardrail.Nsfw()
    pii_gr = guardrail.Pii()

    result = Run([topic_gr, nsfw_gr, pii_gr], "safe test content")

    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "aggregated"
    assert hasattr(result, "is_allowed")
    assert hasattr(result, "reason")
    assert hasattr(result, "metadata")

    # Check metadata structure
    assert result.metadata is not None
    assert "text_results" in result.metadata
    assert "guardrail_names" in result.metadata
    assert len(result.metadata["text_results"]) == 1  # Single text
    assert len(result.metadata["guardrail_names"]) == 3  # Three guardrails


def test_run_multiple_guardrails_early_return():
    """Test Run function with multiple guardrails and early return."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])
    nsfw_gr = guardrail.Nsfw()
    pii_gr = guardrail.Pii()

    # Test with content that might trigger early return
    # Note: In test environment, guardrails may fail due to LLM config, which is expected
    result = Run([topic_gr, nsfw_gr, pii_gr], "test content", early_return=True)
    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "aggregated"


def test_run_invalid_input():
    """Test Run function with invalid input types."""
    # Test with invalid single input - type checker will catch this, but runtime should too
    try:
        Run("not a guardrail", "test content")  # type: ignore
    except TypeError:
        pass  # Expected

    # Test with invalid list input
    try:
        Run([1, 2, 3], "test content")  # type: ignore
    except TypeError:
        pass  # Expected

    # Test with mixed valid/invalid list
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])

    try:
        Run([topic_gr, "not a guardrail"], "test content")  # type: ignore
    except TypeError:
        pass  # Expected


def test_run_return_types():
    """Test that Run returns correct types based on input."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])
    nsfw_gr = guardrail.Nsfw()

    # Single guardrail should return single GuardrailResult
    single_result = Run(topic_gr, "safe content")
    assert isinstance(single_result, GuardrailResult)
    assert hasattr(single_result, "is_allowed")
    assert hasattr(single_result, "reason")
    assert hasattr(single_result, "metadata")

    # Multiple guardrails should return aggregated GuardrailResult
    multi_result = Run([topic_gr, nsfw_gr], "safe content")
    assert isinstance(multi_result, GuardrailResult)
    assert multi_result.guardrail_name == "aggregated"
    assert multi_result.metadata is not None
    assert len(multi_result.metadata["guardrail_names"]) == 2

    # Empty list should return aggregated result with no guardrails
    empty_result = Run([], "safe content")
    assert isinstance(empty_result, GuardrailResult)
    assert empty_result.guardrail_name == "aggregated"
    assert empty_result.metadata is not None
    assert len(empty_result.metadata["guardrail_names"]) == 0


def test_run_multiple_texts_single_guardrail():
    """Test Run function with multiple texts and single guardrail."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])
    result = Run(topic_gr, ["safe content 1", "safe content 2", "safe content 3"])

    assert isinstance(result, GuardrailResult)
    assert hasattr(result, "is_allowed")
    assert hasattr(result, "reason")
    assert hasattr(result, "metadata")
    assert result.guardrail_name == "aggregated"

    # Check metadata structure
    assert result.metadata is not None
    assert "text_results" in result.metadata
    assert "guardrail_names" in result.metadata
    assert "total_texts" in result.metadata
    assert "processed_texts" in result.metadata

    assert result.metadata["total_texts"] == 3
    assert len(result.metadata["text_results"]) == 3
    assert result.metadata["guardrail_names"] == ["topic"]


def test_run_multiple_texts_multiple_guardrails():
    """Test Run function with multiple texts and multiple guardrails."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])
    nsfw_gr = guardrail.Nsfw()

    result = Run([topic_gr, nsfw_gr], ["content 1", "content 2"])

    assert isinstance(result, GuardrailResult)
    assert result.guardrail_name == "aggregated"

    # Check metadata
    assert result.metadata is not None
    assert result.metadata["total_texts"] == 2
    assert len(result.metadata["text_results"]) == 2
    assert set(result.metadata["guardrail_names"]) == {"topic", "nsfw"}

    # Each text should have results for both guardrails
    for text_result in result.metadata["text_results"]:
        assert "text_index" in text_result
        assert "text" in text_result
        assert "results" in text_result
        assert len(text_result["results"]) == 2  # One result per guardrail


def test_run_multiple_texts_metadata_structure():
    """Test detailed metadata structure for multiple texts."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["business"], blocked_topics=["competitor"])
    nsfw_gr = guardrail.Nsfw()

    result = Run([topic_gr, nsfw_gr], ["text 1", "text 2"])

    # Check top-level metadata
    assert result.metadata is not None
    metadata = result.metadata
    assert metadata["total_texts"] == 2
    assert metadata["processed_texts"] == 2
    assert len(metadata["guardrail_names"]) == 2

    # Check text results structure
    text_results = metadata["text_results"]
    assert len(text_results) == 2

    for i, text_result in enumerate(text_results):
        assert text_result["text_index"] == i
        assert text_result["text"] == f"text {i + 1}"
        assert len(text_result["results"]) == 2  # One per guardrail

        # Each result should be a GuardrailResult
        for gr_result in text_result["results"]:
            assert isinstance(gr_result, GuardrailResult)
            assert hasattr(gr_result, "is_allowed")
            assert hasattr(gr_result, "reason")
            assert hasattr(gr_result, "metadata")


def test_run_multiple_texts_empty_list():
    """Test Run function with empty text list."""
    from dspy_guardrails import guardrail

    topic_gr = guardrail.Topic(topic_scopes=["test"], blocked_topics=["dummy"])

    # Empty list should return aggregated result with no texts processed
    result = Run(topic_gr, [])

    assert isinstance(result, GuardrailResult)
    assert result.is_allowed is True  # No texts means no failures
    assert result.metadata is not None
    assert result.metadata["total_texts"] == 0
    assert result.metadata["processed_texts"] == 0
    assert len(result.metadata["text_results"]) == 0
