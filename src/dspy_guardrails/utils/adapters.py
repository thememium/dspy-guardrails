"""Caching DSPy adapter for guardrails."""

from functools import lru_cache

import dspy


class GuardrailJSONAdapter(dspy.JSONAdapter):
    """``dspy.JSONAdapter`` with signature-derived prompt fragments cached.

    ``format_system_message`` and ``user_message_output_requirements`` are
    pure functions of the signature class, but dspy rebuilds them on every
    call -- including a ``pydantic.TypeAdapter`` and JSON-schema generation
    per field. Guardrails invoke the LM per check, so those rebuilds
    dominate per-request latency. Caching by signature is safe: each
    guardrail compiles one fixed signature, and the fragments never depend
    on runtime inputs.
    """

    @lru_cache(maxsize=128)
    def format_system_message(self, signature):
        return super().format_system_message(signature)

    @lru_cache(maxsize=128)
    def user_message_output_requirements(self, signature):
        return super().user_message_output_requirements(signature)
