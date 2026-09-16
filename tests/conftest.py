import dspy
import pytest


@pytest.fixture(scope="session", autouse=True)
def configure_guardrails():
    from dspy_guardrails import configure

    lm = dspy.LM("openrouter/openai/gpt-oss-120b:nitro")
    configure(lm=lm)
