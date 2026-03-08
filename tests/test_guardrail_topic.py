from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail


def test_topic_guardrail_type():
    guard = guardrail.Topic(
        topic_scopes=["AI", "Machine Learning"],
        blocked_topics=["spam"],
    )

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "topic"
    assert guard.config.topic_scopes == ["AI", "Machine Learning"]
    assert guard.config.blocked_topics == ["spam"]
