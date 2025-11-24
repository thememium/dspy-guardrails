"""DSPy Guardrails - AI content moderation and security guardrails.

A Python package that provides programmatic access to DSPy-based guardrails
for content moderation, security filtering, and compliance checking.
"""

from . import guardrail
from .core import BaseGuardrail, GuardrailResult
from .core.config import configure
from .guardrail import Run
from .guardrails import (
    JailbreakGuardrail,
    KeywordsGuardrail,
    NsfwGuardrail,
    PiiGuardrail,
    PromptInjectionGuardrail,
    SecretKeysGuardrail,
    TopicGuardrail,
)

__version__ = "0.1.0"
__all__ = [
    "guardrail",
    "BaseGuardrail",
    "GuardrailResult",
    "configure",
    "Run",
    "TopicGuardrail",
    "NsfwGuardrail",
    "JailbreakGuardrail",
    "PiiGuardrail",
    "PromptInjectionGuardrail",
    "KeywordsGuardrail",
    "SecretKeysGuardrail",
]
