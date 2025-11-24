"""DSPy Guardrails - AI content moderation and security guardrails.

A Python package that provides programmatic access to DSPy-based guardrails
for content moderation, security filtering, and compliance checking.
"""

from .core import BaseGuardrail, GuardrailManager, GuardrailResult
from .factory import (create_comprehensive_guardrail_suite,
                      create_jailbreak_guardrail, create_keywords_guardrail,
                      create_nsfw_guardrail, create_pii_guardrail,
                      create_prompt_injection_guardrail,
                      create_secret_keys_guardrail, create_topic_guardrail)
from .guardrails import (JailbreakGuardrail, KeywordsGuardrail, NsfwGuardrail,
                         PiiGuardrail, PromptInjectionGuardrail,
                         SecretKeysGuardrail, TopicGuardrail)

__version__ = "0.1.0"
__all__ = [
    "BaseGuardrail",
    "GuardrailResult",
    "GuardrailManager",
    "create_topic_guardrail",
    "create_nsfw_guardrail",
    "create_jailbreak_guardrail",
    "create_pii_guardrail",
    "create_keywords_guardrail",
    "create_prompt_injection_guardrail",
    "create_secret_keys_guardrail",
    "create_comprehensive_guardrail_suite",
    "TopicGuardrail",
    "NsfwGuardrail",
    "JailbreakGuardrail",
    "PiiGuardrail",
    "PromptInjectionGuardrail",
    "KeywordsGuardrail",
    "SecretKeysGuardrail",
]
