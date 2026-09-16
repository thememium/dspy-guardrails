"""Tests for dspy_guardrails.core.base."""

from typing import Any, cast

import pytest

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import GuardrailConfig


class _StubGuardrail(BaseGuardrail):
    """Minimal concrete guardrail used to exercise BaseGuardrail behavior."""

    @property
    def name(self) -> str:
        return "stub"

    def _configure_dspy(self) -> None:
        pass

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        return GuardrailResult(
            is_allowed=True,
            guardrail_name=self.name,
            metadata=dict(kwargs) or None,
        )


# --- GuardrailResult ------------------------------------------------------


def test_result_metadata_defaults_to_empty_dict():
    result = GuardrailResult(is_allowed=True)
    assert result.metadata == {}
    assert result.reason is None
    assert result.guardrail_name == ""


def test_result_rejects_non_boolean_is_allowed():
    non_bool: Any = cast(Any, "yes")
    with pytest.raises(ValueError, match="is_allowed must be a boolean"):
        GuardrailResult(is_allowed=non_bool)
    non_bool = cast(Any, 1)
    with pytest.raises(ValueError, match="is_allowed must be a boolean"):
        GuardrailResult(is_allowed=non_bool)


def test_result_keeps_explicit_metadata():
    result = GuardrailResult(is_allowed=False, metadata={"score": 0.9})
    assert result.metadata == {"score": 0.9}


# --- BaseGuardrail ---------------------------------------------------------


def test_base_guardrail_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseGuardrail(config=GuardrailConfig())


def test_concrete_subclass_uses_base_init():
    guard = _StubGuardrail(GuardrailConfig())
    assert isinstance(guard.config, GuardrailConfig)


def test_check_batch_maps_results_and_forwards_kwargs():
    guard = _StubGuardrail(GuardrailConfig())
    results = guard.check_batch(["alpha", "beta", "gamma"], channel="web")
    assert [r.is_allowed for r in results] == [True, True, True]
    assert all(r.metadata == {"channel": "web"} for r in results)
    assert all(r.guardrail_name == "stub" for r in results)


def test_check_batch_empty_input_returns_empty_list():
    guard = _StubGuardrail(GuardrailConfig())
    assert guard.check_batch([]) == []


def test_repr_includes_class_name_and_config():
    guard = _StubGuardrail(GuardrailConfig())
    assert repr(guard) == f"_StubGuardrail(config={guard.config!r})"


# The abstract bodies in BaseGuardrail are executable no-ops (`pass`); call
# them directly to lock in that contract.


def test_abstract_name_body_is_noop():
    guard = _StubGuardrail(GuardrailConfig())
    assert BaseGuardrail.name.fget(guard) is None


def test_abstract_configure_dspy_body_is_noop():
    guard = _StubGuardrail(GuardrailConfig())
    assert BaseGuardrail._configure_dspy(guard) is None


def test_abstract_check_body_is_noop():
    guard = _StubGuardrail(GuardrailConfig())
    assert BaseGuardrail.check(guard, "hello") is None
