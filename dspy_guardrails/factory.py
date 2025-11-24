"""Factory functions for creating guardrails with common configurations."""

from typing import List, Optional

from dspy_guardrails.core.config import (
    JailbreakGuardrailConfig,
    KeywordsGuardrailConfig,
    NsfwGuardrailConfig,
    PiiGuardrailConfig,
    PromptInjectionGuardrailConfig,
    SecretKeysGuardrailConfig,
    TopicGuardrailConfig,
)
from dspy_guardrails.guardrails import (
    JailbreakGuardrail,
    KeywordsGuardrail,
    NsfwGuardrail,
    PiiGuardrail,
    PromptInjectionGuardrail,
    SecretKeysGuardrail,
    TopicGuardrail,
)


def create_topic_guardrail(
    business_scopes: List[str],
    competitor_names: Optional[List[str]] = None,
) -> TopicGuardrail:
    """Create a topic compliance guardrail with the specified configuration.

    Note: DSPy must be configured globally before using this guardrail.
    Use dspy.configure(lm=your_lm) to set up DSPy.

    Args:
        business_scopes: List of business topics that are considered on-topic
        competitor_names: List of competitor names to flag (optional)

    Returns:
        Configured TopicGuardrail instance

    Example:
        import dspy

        # Configure DSPy first
        dspy.configure(lm=dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key"))

        # Create guardrail
        guardrail = create_topic_guardrail(
            business_scopes=["Shipping", "Logistics", "E-commerce"],
            competitor_names=["CompetitorA", "CompetitorB"]
        )
    """
    if competitor_names is None:
        competitor_names = []

    config = TopicGuardrailConfig(
        business_scopes=business_scopes,
        competitor_names=competitor_names,
    )
    return TopicGuardrail(config)


def create_nsfw_guardrail(
    sensitivity_level: str = "medium",
) -> NsfwGuardrail:
    """Create an NSFW content detection guardrail.

    Note: DSPy must be configured globally before using this guardrail.
    Use dspy.configure(lm=your_lm) to set up DSPy.

    Args:
        sensitivity_level: Sensitivity level ("low", "medium", "high")

    Returns:
        Configured NsfwGuardrail instance
    """
    config = NsfwGuardrailConfig(
        sensitivity_level=sensitivity_level,
    )
    return NsfwGuardrail(config)


def create_jailbreak_guardrail(
    detection_threshold: float = 0.8,
) -> JailbreakGuardrail:
    """Create a jailbreak detection guardrail.

    Note: DSPy must be configured globally before using this guardrail.
    Use dspy.configure(lm=your_lm) to set up DSPy.

    Args:
        detection_threshold: Confidence threshold for flagging jailbreaks (0.0-1.0)

    Returns:
        Configured JailbreakGuardrail instance
    """
    config = JailbreakGuardrailConfig(
        detection_threshold=detection_threshold,
    )
    return JailbreakGuardrail(config)


def create_pii_guardrail(
    allowed_pii_types: Optional[List[str]] = None,
) -> PiiGuardrail:
    """Create a PII detection guardrail.

    Note: DSPy must be configured globally before using this guardrail.
    Use dspy.configure(lm=your_lm) to set up DSPy.

    Args:
        allowed_pii_types: List of PII types that are allowed (None means all PII blocked)

    Returns:
        Configured PiiGuardrail instance
    """
    config = PiiGuardrailConfig(
        allowed_pii_types=allowed_pii_types,
    )
    return PiiGuardrail(config)


def create_keywords_guardrail(
    blocked_keywords: List[str],
    case_sensitive: bool = False,
) -> KeywordsGuardrail:
    """Create a keyword filtering guardrail.

    Note: DSPy must be configured globally before using this guardrail.
    Use dspy.configure(lm=your_lm) to set up DSPy.

    Args:
        blocked_keywords: List of keywords to block
        case_sensitive: Whether keyword matching is case sensitive

    Returns:
        Configured KeywordsGuardrail instance
    """
    config = KeywordsGuardrailConfig(
        blocked_keywords=blocked_keywords,
        case_sensitive=case_sensitive,
    )
    return KeywordsGuardrail(config)


def create_prompt_injection_guardrail(
    injection_patterns: Optional[List[str]] = None,
) -> PromptInjectionGuardrail:
    """Create a prompt injection detection guardrail.

    Note: DSPy must be configured globally before using this guardrail.
    Use dspy.configure(lm=your_lm) to set up DSPy.

    Args:
        injection_patterns: Custom injection patterns to detect (optional)

    Returns:
        Configured PromptInjectionGuardrail instance
    """
    config = PromptInjectionGuardrailConfig(
        injection_patterns=injection_patterns,
    )
    return PromptInjectionGuardrail(config)


def create_secret_keys_guardrail(
    key_patterns: Optional[List[str]] = None,
    entropy_threshold: float = 4.0,
) -> SecretKeysGuardrail:
    """Create a secret keys detection guardrail.

    Note: DSPy must be configured globally before using this guardrail.
    Use dspy.configure(lm=your_lm) to set up DSPy.

    Args:
        key_patterns: Custom key patterns to detect (optional)
        entropy_threshold: Minimum entropy for potential secrets

    Returns:
        Configured SecretKeysGuardrail instance
    """
    config = SecretKeysGuardrailConfig(
        key_patterns=key_patterns,
        entropy_threshold=entropy_threshold,
    )
    return SecretKeysGuardrail(config)
