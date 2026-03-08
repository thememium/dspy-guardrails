import dspy
import pytest


@pytest.fixture(scope="session", autouse=True)
def configure_guardrails():
    from dspy_guardrails import configure

    lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025")
    configure(lm=lm)
