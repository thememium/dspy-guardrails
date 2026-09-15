"""Caching DSPy adapter for guardrails."""

import enum
from functools import lru_cache
from typing import Any, Literal, cast, get_origin

import dspy
import json_repair
import regex
from dspy.adapters.utils import parse_value
from dspy.utils.exceptions import AdapterParseError
from pydantic import TypeAdapter


@lru_cache(maxsize=256)
def _cached_type_adapter(annotation) -> TypeAdapter:
    """Cache ``TypeAdapter`` construction per annotation.

    dspy's ``parse_value`` constructs a ``TypeAdapter`` (compiling a
    pydantic core schema) on every output-field cast; guardrail signatures
    are fixed, so the adapters are trivially cacheable.
    """
    return TypeAdapter(annotation)


def _parse_field_value(value: Any, annotation) -> Any:
    """Cast one LM output value, preserving ``dspy.parse_value`` semantics.

    dspy's implementation special-cases strings (JSON-repair, Literal
    munging, enums, unions with ``None``) and constructs a fresh
    ``TypeAdapter`` per call. Strings and the special-cased annotations are
    routed to ``parse_value`` unchanged; everything else takes the cached
    adapter, which performs the identical ``validate_python`` call dspy
    would for non-string values.
    """
    if (
        isinstance(value, str)
        or annotation is str
        or isinstance(annotation, enum.EnumMeta)
        or get_origin(annotation) is Literal
    ):
        return parse_value(value, annotation)
    return _cached_type_adapter(annotation).validate_python(value)


class GuardrailJSONAdapter(dspy.JSONAdapter):
    """``dspy.JSONAdapter`` with per-check overhead cached.

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

    def parse(self, signature, completion: str) -> dict[str, Any]:
        """Parse an LM completion, mirroring ``JSONAdapter.parse`` with a
        cached per-annotation TypeAdapter for output-field casting."""
        fields = json_repair.loads(completion)

        if not isinstance(fields, dict):
            pattern = r"\{(?:[^{}]|(?R))*\}"
            match = regex.search(pattern, completion, regex.DOTALL)
            if match:
                completion = match.group(0)
                fields = json_repair.loads(completion)

        if not isinstance(fields, dict):
            raise AdapterParseError(
                adapter_name="JSONAdapter",
                signature=signature,
                lm_response=completion,
                message="LM response cannot be serialized to a JSON object.",
            )

        output_fields = signature.output_fields
        fields = {k: v for k, v in fields.items() if k in output_fields}

        for k, v in fields.items():
            fields[k] = _parse_field_value(v, output_fields[k].annotation)

        if fields.keys() != output_fields.keys():
            raise AdapterParseError(
                adapter_name="JSONAdapter",
                signature=signature,
                lm_response=completion,
                parsed_result=cast(Any, fields),
            )

        return fields
