"""Tests for ``dspy_guardrails.utils.adapters.GuardrailJSONAdapter``.

Exercises the cached-formatting helpers and the ``parse`` fallback/error
branches directly, the way dspy invokes them.
"""

import json

import dspy
import pydantic
import pytest
from dspy.adapters.chat_adapter import FieldInfoWithName
from dspy.utils.exceptions import AdapterParseError

from dspy_guardrails.utils.adapters import (
    GuardrailJSONAdapter,
    _format_field_value_cached,
    _serialize_for_json_cached,
)


class GuardCheck(dspy.Signature):
    """Check the text against the policy."""

    text: str = dspy.InputField()
    is_bad: bool = dspy.OutputField()


@pytest.fixture
def adapter():
    return GuardrailJSONAdapter()


# --------------------------------------------------------------------------- #
# Cached serialization helpers                                                 #
# --------------------------------------------------------------------------- #


class NotSerializable:
    """A plain class pydantic cannot build a schema for."""


def test_serialize_falls_back_to_str_for_unserializable_value():
    value = NotSerializable()
    assert _serialize_for_json_cached(value) == str(value)


def test_serialize_roundtrips_jsonable_value():
    assert _serialize_for_json_cached({"a": 1}) == {"a": 1}
    assert _serialize_for_json_cached(True) is True


def test_format_field_value_serializes_list_for_str_annotation():
    field_info = pydantic.fields.FieldInfo(annotation=str)
    assert (
        _format_field_value_cached(field_info, ["alpha", "beta"])
        == "[1] «alpha»\n[2] «beta»"
    )
    assert _format_field_value_cached(field_info, []) == "N/A"


def test_format_field_value_dumps_dict_as_json():
    field_info = pydantic.fields.FieldInfo(annotation=dict)
    out = _format_field_value_cached(field_info, {"a": 1})
    assert json.loads(out) == {"a": 1}


# --------------------------------------------------------------------------- #
# Formatting entry points                                                      #
# --------------------------------------------------------------------------- #


def test_format_user_message_content_formats_list_input(adapter):
    out = adapter.format_user_message_content(GuardCheck, {"text": ["one", "two"]})
    assert out == "[[ ## text ## ]]\n[1] «one»\n[2] «two»"


def test_format_user_message_content_skips_missing_inputs(adapter):
    out = adapter.format_user_message_content(GuardCheck, {}, suffix="done")
    assert out == "done"


def test_format_field_with_value_user_role_with_list_value(adapter):
    fields = {
        FieldInfoWithName(
            name="text", info=pydantic.fields.FieldInfo(annotation=str)
        ): ["a", "b"]
    }
    out = adapter.format_field_with_value(fields)
    assert out == "[[ ## text ## ]]\n[1] «a»\n[2] «b»"


def test_format_field_with_value_assistant_role_dumps_json(adapter):
    fields = {
        FieldInfoWithName(
            name="is_bad", info=pydantic.fields.FieldInfo(annotation=bool)
        ): True
    }
    out = adapter.format_field_with_value(fields, role="assistant")
    assert json.loads(out) == {"is_bad": True}


# --------------------------------------------------------------------------- #
# parse()                                                                      #
# --------------------------------------------------------------------------- #


def test_parse_casts_output_fields(adapter):
    assert adapter.parse(GuardCheck, '{"is_bad": true}') == {"is_bad": True}


def test_parse_extracts_json_object_from_surrounding_text(adapter):
    """When the completion is not a top-level JSON object, the adapter must
    recover the embedded object and parse it."""
    completion = 'Answer:\n[{"is_bad": true}]'
    assert adapter.parse(GuardCheck, completion) == {"is_bad": True}


def test_parse_raises_when_no_json_object_present(adapter):
    with pytest.raises(AdapterParseError, match="cannot be serialized"):
        adapter.parse(GuardCheck, "no structured output here")


def test_parse_raises_when_output_field_missing(adapter):
    with pytest.raises(AdapterParseError):
        adapter.parse(GuardCheck, '{"other_field": true}')
