"""DSPy Guardrails - AI content moderation and security guardrails.

A Python package that provides programmatic access to DSPy-based guardrails
for content moderation, security filtering, and compliance checking.
"""

from . import guardrail
from .core import BaseGuardrail, GuardrailResult
from .core.config import configure
from .guardrail import (
    Gibberish,
    Grounding,
    Jailbreak,
    Keywords,
    Language,
    Nsfw,
    Pii,
    PromptInjection,
    Run,
    SecretKeys,
    Tone,
    Topic,
    Toxicity,
)
from .guardrails import (
    GibberishGuardrail,
    GroundingGuardrail,
    JailbreakGuardrail,
    KeywordsGuardrail,
    LanguageGuardrail,
    NsfwGuardrail,
    PiiGuardrail,
    PromptInjectionGuardrail,
    SecretKeysGuardrail,
    ToneGuardrail,
    TopicGuardrail,
    ToxicityGuardrail,
)

__version__ = "0.1.0"
__all__ = [
    "guardrail",
    "BaseGuardrail",
    "GuardrailResult",
    "configure",
    "Run",
    "Topic",
    "Nsfw",
    "Jailbreak",
    "Pii",
    "PromptInjection",
    "Keywords",
    "SecretKeys",
    "Toxicity",
    "Gibberish",
    "Language",
    "Tone",
    "Grounding",
    "TopicGuardrail",
    "NsfwGuardrail",
    "JailbreakGuardrail",
    "PiiGuardrail",
    "PromptInjectionGuardrail",
    "KeywordsGuardrail",
    "SecretKeysGuardrail",
    "ToxicityGuardrail",
    "GibberishGuardrail",
    "LanguageGuardrail",
    "ToneGuardrail",
    "GroundingGuardrail",
]
