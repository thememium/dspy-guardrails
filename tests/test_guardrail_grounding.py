from unittest.mock import MagicMock, patch

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult


def test_grounding_guardrail_type():
    guard = guardrail.Grounding(grounding_threshold=0.9)

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "grounding"
    assert guard.config.grounding_threshold == 0.9


# --------------------------------------------------------------------------- #
# check() branches                                                             #
# --------------------------------------------------------------------------- #


def _mock_grounding_result(**overrides):
    mock = MagicMock()
    mock.is_grounded = overrides.get("is_grounded", True)
    mock.grounding_score = overrides.get("grounding_score", 0.95)
    mock.hallucinations = overrides.get("hallucinations", [])
    mock.reason = overrides.get("reason")
    return mock


def test_check_returns_failure_when_dspy_not_configured():
    guard = guardrail.Grounding()
    with patch(
        "dspy_guardrails.guardrails.grounding.is_dspy_configured",
        return_value=False,
    ):
        result = guard.check("the answer", context="some context")

    assert isinstance(result, GuardrailResult)
    assert result.is_allowed is False
    assert "not properly configured" in (result.reason or "")
    assert (result.metadata or {}).get("error") == "DSPy not configured"


def test_check_requires_context_kwarg():
    guard = guardrail.Grounding()
    result = guard.check("the answer")

    assert result.is_allowed is False
    assert "context" in (result.reason or "")
    assert (result.metadata or {}).get("error") == "Missing context"


def test_check_flags_ungrounded_answer_with_hallucinations():
    guard = guardrail.Grounding(grounding_threshold=0.7)
    mock_result = _mock_grounding_result(
        is_grounded=False,
        grounding_score=0.4,
        hallucinations=["the moon is made of cheese"],
        reason="Unsupported claim found",
    )
    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("the moon is made of cheese", context="space facts")

    assert result.is_allowed is False
    assert "Unsupported claim found" in (result.reason or "")
    assert "the moon is made of cheese" in (result.reason or "")
    metadata = result.metadata or {}
    assert metadata["grounding_score"] == 0.4
    assert metadata["is_grounded"] is False
    assert metadata["hallucinations"] == ["the moon is made of cheese"]
    assert metadata["threshold"] == 0.7


def test_check_flags_below_threshold_with_fallback_reason():
    """Score below threshold with no LLM explanation -> generic reason."""
    guard = guardrail.Grounding(grounding_threshold=0.7)
    mock_result = _mock_grounding_result(
        is_grounded=True,
        grounding_score=0.5,
        hallucinations=[],
        reason=None,
    )
    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("shaky answer", context="solid context")

    assert result.is_allowed is False
    assert "Factual grounding failed" in (result.reason or "")


def test_check_allows_grounded_answer():
    guard = guardrail.Grounding(grounding_threshold=0.7)
    mock_result = _mock_grounding_result(
        is_grounded=True,
        grounding_score=0.95,
        hallucinations=[],
        reason="Well supported",
    )
    with patch.object(guard, "_run_program", return_value=mock_result):
        result = guard.check("grounded answer", context="reference text")

    assert result.is_allowed is True
    assert result.reason is None
    metadata = result.metadata or {}
    assert metadata["grounding_score"] == 0.95
    assert metadata["is_grounded"] is True


def test_check_returns_error_result_on_exception():
    guard = guardrail.Grounding()
    with patch.object(guard, "_run_program", side_effect=RuntimeError("boom")):
        result = guard.check("the answer", context="the context")

    assert result.is_allowed is False
    assert "Error during grounding check" in (result.reason or "")
    assert "boom" in (result.reason or "")
    assert (result.metadata or {}).get("error") == "boom"
