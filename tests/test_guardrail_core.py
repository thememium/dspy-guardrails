"""Tests for ``dspy_guardrails.guardrail`` module-level orchestration.

Covers branches of ``Run`` and ``_run_aggregated`` not exercised by the
guardrail-specific suites: input validation, the ``configure`` delegation,
and the sequential early-return break paths.
"""

from typing import Any, cast
from unittest.mock import patch

import pytest

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult

# --------------------------------------------------------------------------- #
# Stubs                                                                        #
# --------------------------------------------------------------------------- #


class StubGuardrail(BaseGuardrail):
    """Minimal guardrail double that returns a canned ``GuardrailResult``."""

    def __init__(self, name="stub", result=None):
        self._name = name
        self._result = result or GuardrailResult(
            is_allowed=True, reason=None, guardrail_name=name
        )
        self.calls = []

    @property
    def name(self):
        return self._name

    def _configure_dspy(self):
        pass  # global DSPy already configured by the session fixture

    def check(self, input_text, **kwargs):
        self.calls.append((input_text, kwargs))
        return self._result


def make_result(allowed, reason=None, name="stub"):
    return GuardrailResult(is_allowed=allowed, reason=reason, guardrail_name=name)


# --------------------------------------------------------------------------- #
# configure() delegation                                                       #
# --------------------------------------------------------------------------- #


def test_configure_delegates_to_core_configure():
    with patch.object(
        guardrail, "_configure", return_value="sentinel"
    ) as mock_configure:
        out = guardrail.configure(lm="fake-lm", temperature=0.2)
    assert out == "sentinel"
    mock_configure.assert_called_once_with(lm="fake-lm", temperature=0.2)


# --------------------------------------------------------------------------- #
# Factory defaults                                                             #
# --------------------------------------------------------------------------- #


def test_topic_defaults_blocked_topics_to_empty_list():
    gr = guardrail.Topic(topic_scopes=["AI", "Machine Learning"])
    assert gr.config.blocked_topics == []
    assert gr.config.topic_scopes == ["AI", "Machine Learning"]


# --------------------------------------------------------------------------- #
# Run() input validation                                                       #
# --------------------------------------------------------------------------- #


def test_run_rejects_non_guardrail_input():
    with pytest.raises(
        TypeError, match="guardrails must be a BaseGuardrail instance or sequence"
    ):
        guardrail.Run(cast(Any, 42), "hello")


def test_run_rejects_non_guardrail_in_sequence():
    with pytest.raises(
        TypeError, match="All items in guardrails list must be BaseGuardrail"
    ):
        guardrail.Run([StubGuardrail(), cast(Any, 42)], "hello")


def test_run_rejects_invalid_text_type():
    with pytest.raises(TypeError, match="text must be a string or list of strings"):
        guardrail.Run(StubGuardrail(), cast(Any, 42))


# --------------------------------------------------------------------------- #
# Sequential early-return break paths                                          #
# --------------------------------------------------------------------------- #


def test_sequential_early_return_skips_remaining_guardrails_and_texts():
    """A failing first guardrail must short-circuit both loops: no later
    guardrail runs for that text and no later text is processed."""
    fail = StubGuardrail(
        name="fail", result=make_result(False, reason="blocked", name="fail")
    )
    ok = StubGuardrail(name="ok", result=make_result(True, name="ok"))

    result = guardrail.Run([fail, ok], ["bad", "good"], early_return=True)

    assert result.is_allowed is False
    assert result.reason == "blocked"
    md = result.metadata or {}
    assert md["processed_texts"] == 1
    assert md["total_texts"] == 2
    assert len(md["text_results"][0]["results"]) == 1  # only the first guardrail ran
    assert fail.calls == [("bad", {})]
    assert ok.calls == []  # never reached


def test_sequential_early_return_stops_at_failing_guardrail_mid_list():
    """With early_return, later guardrails run until one fails; the failing
    result is recorded and no further text is processed."""
    ok = StubGuardrail(name="ok", result=make_result(True, name="ok"))
    fail = StubGuardrail(
        name="fail", result=make_result(False, reason="nsfw hit", name="fail")
    )

    result = guardrail.Run([ok, fail], ["clean", "dirty", "more"], early_return=True)

    assert result.is_allowed is False
    assert result.reason == "nsfw hit"
    md = result.metadata or {}
    assert md["processed_texts"] == 1
    assert md["total_texts"] == 3
    # Both guardrails ran on the first text; the failure is recorded last.
    first_text_results = md["text_results"][0]["results"]
    assert [r.is_allowed for r in first_text_results] == [True, False]
    assert ok.calls == [("clean", {})]
    assert fail.calls == [("clean", {})]


def test_shared_executor_is_reused_across_runs():
    """The default parallel path reuses one process-wide pool instead of
    paying pool creation/teardown per Run."""
    first = guardrail._shared_executor()
    second = guardrail._shared_executor()
    assert first is second


def test_parallel_default_path_uses_shared_executor():
    """A parallel Run with no explicit num_threads completes correctly on
    the shared pool and returns the same aggregation as sequential."""
    ok = StubGuardrail(name="ok", result=make_result(True, name="ok"))

    parallel = guardrail.Run([ok], ["a", "b"], parallel=True)
    sequential = guardrail.Run([ok], ["a", "b"])

    assert parallel.is_allowed == sequential.is_allowed
    assert [
        r.is_allowed
        for tr in (parallel.metadata or {})["text_results"]
        for r in tr["results"]
    ] == [True, True]
    md = parallel.metadata or {}
    assert md["num_threads"] is None
