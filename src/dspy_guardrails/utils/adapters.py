"""Caching DSPy adapter for guardrails."""

import enum
import json
from functools import lru_cache
from typing import Any, Literal, cast, get_origin

import dspy
import json_repair
import regex
from dspy.adapters.utils import _format_input_list_field_value, parse_value
from dspy.utils.exceptions import AdapterParseError
from pydantic import TypeAdapter


@lru_cache(maxsize=256)
def _cached_type_adapter(annotation) -> TypeAdapter:
    """Cache ``TypeAdapter`` construction per annotation.

    dspy constructs a fresh ``TypeAdapter`` (compiling a pydantic core
    schema) for every field value it serializes and every output field it
    casts, on every LM call. Guardrail signatures and value types are
    fixed, so the adapters are trivially cacheable.
    """
    return TypeAdapter(annotation)


def _serialize_for_json_cached(value: Any) -> Any:
    """``dspy.adapters.utils.serialize_for_json`` with a cached TypeAdapter.

    Semantics are identical: same ``dump_python(mode="json")`` call, same
    string fallback when pydantic cannot serialize the value.
    """
    try:
        return _cached_type_adapter(type(value)).dump_python(value, mode="json")
    except Exception:
        return str(value)


def _format_field_value_cached(field_info, value: Any) -> str:
    """``dspy.adapters.utils.format_field_value`` using the cached
    serializer (see ``_serialize_for_json_cached``)."""
    if isinstance(value, list) and field_info.annotation is str:
        return _format_input_list_field_value(value)
    jsonable_value = _serialize_for_json_cached(value)
    if isinstance(jsonable_value, (dict, list)):
        return json.dumps(jsonable_value, ensure_ascii=False)
    return str(jsonable_value)


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

    def format_user_message_content(
        self,
        signature,
        inputs,
        prefix: str = "",
        suffix: str = "",
        main_request: bool = False,
    ) -> str:
        """``ChatAdapter.format_user_message_content`` with cached field
        serialization (see ``_format_field_value_cached``)."""
        messages = [prefix]
        for k, v in signature.input_fields.items():
            if k in inputs:
                formatted_field_value = _format_field_value_cached(
                    field_info=v, value=inputs.get(k)
                )
                messages.append(f"[[ ## {k} ## ]]\n{formatted_field_value}")

        if main_request:
            output_requirements = self.user_message_output_requirements(signature)
            if output_requirements is not None:
                messages.append(output_requirements)

        messages.append(suffix)
        return "\n\n".join(messages).strip()

    def format_field_with_value(self, fields_with_values, role: str = "user") -> str:
        """``JSONAdapter.format_field_with_value`` with cached field
        serialization (see ``_serialize_for_json_cached``)."""
        if role == "user":
            output = []
            for field, field_value in fields_with_values.items():
                formatted_field_value = _format_field_value_cached(
                    field_info=field.info, value=field_value
                )
                output.append(f"[[ ## {field.name} ## ]]\n{formatted_field_value}")
            return "\n\n".join(output).strip()

        d = fields_with_values.items()
        d = {k.name: v for k, v in d}
        return json.dumps(_serialize_for_json_cached(d), indent=2)

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
