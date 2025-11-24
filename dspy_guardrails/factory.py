"""Factory functions for creating guardrails with common configurations."""

from typing import List, Optional

from dspy_guardrails.core.config import (JailbreakGuardrailConfig,
                                         KeywordsGuardrailConfig,
                                         NsfwGuardrailConfig,
                                         PiiGuardrailConfig,
                                         PromptInjectionGuardrailConfig,
                                         SecretKeysGuardrailConfig,
                                         TopicGuardrailConfig)
from dspy_guardrails.guardrails import (JailbreakGuardrail, KeywordsGuardrail,
                                        NsfwGuardrail, PiiGuardrail,
                                        PromptInjectionGuardrail,
                                        SecretKeysGuardrail, TopicGuardrail)


def create_topic_guardrail(
    business_scopes: List[str],
    competitor_names: Optional[List[str]] = None,
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
) -> TopicGuardrail:
    """Create a topic compliance guardrail with the specified configuration.

    Args:
        business_scopes: List of business topics that are considered on-topic
        competitor_names: List of competitor names to flag (optional)
        model: DSPy model to use for the guardrail

    Returns:
        Configured TopicGuardrail instance

    Example:
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
        model=model,
    )
    return TopicGuardrail(config)


def create_nsfw_guardrail(
    sensitivity_level: str = "medium",
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
) -> NsfwGuardrail:
    """Create an NSFW content detection guardrail.

    Args:
        sensitivity_level: Sensitivity level ("low", "medium", "high")
        model: DSPy model to use for the guardrail

    Returns:
        Configured NsfwGuardrail instance
    """
    config = NsfwGuardrailConfig(
        sensitivity_level=sensitivity_level,
        model=model,
    )
    return NsfwGuardrail(config)


def create_jailbreak_guardrail(
    detection_threshold: float = 0.8,
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
) -> JailbreakGuardrail:
    """Create a jailbreak detection guardrail.

    Args:
        detection_threshold: Confidence threshold for flagging jailbreaks (0.0-1.0)
        model: DSPy model to use for the guardrail

    Returns:
        Configured JailbreakGuardrail instance
    """
    config = JailbreakGuardrailConfig(
        detection_threshold=detection_threshold,
        model=model,
    )
    return JailbreakGuardrail(config)


def create_pii_guardrail(
    allowed_pii_types: Optional[List[str]] = None,
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
) -> PiiGuardrail:
    """Create a PII detection guardrail.

    Args:
        allowed_pii_types: List of PII types that are allowed (None means all PII blocked)
        model: DSPy model to use for the guardrail

    Returns:
        Configured PiiGuardrail instance
    """
    config = PiiGuardrailConfig(
        allowed_pii_types=allowed_pii_types,
        model=model,
    )
    return PiiGuardrail(config)


def create_keywords_guardrail(
    blocked_keywords: List[str],
    case_sensitive: bool = False,
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
) -> KeywordsGuardrail:
    """Create a keyword filtering guardrail.

    Args:
        blocked_keywords: List of keywords to block
        case_sensitive: Whether keyword matching is case sensitive
        model: DSPy model to use for the guardrail

    Returns:
        Configured KeywordsGuardrail instance
    """
    config = KeywordsGuardrailConfig(
        blocked_keywords=blocked_keywords,
        case_sensitive=case_sensitive,
        model=model,
    )
    return KeywordsGuardrail(config)


def create_prompt_injection_guardrail(
    injection_patterns: Optional[List[str]] = None,
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
) -> PromptInjectionGuardrail:
    """Create a prompt injection detection guardrail.

    Args:
        injection_patterns: Custom injection patterns to detect (optional)
        model: DSPy model to use for the guardrail

    Returns:
        Configured PromptInjectionGuardrail instance
    """
    config = PromptInjectionGuardrailConfig(
        injection_patterns=injection_patterns,
        model=model,
    )
    return PromptInjectionGuardrail(config)


def create_secret_keys_guardrail(
    key_patterns: Optional[List[str]] = None,
    entropy_threshold: float = 4.0,
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
) -> SecretKeysGuardrail:
    """Create a secret keys detection guardrail.

    Args:
        key_patterns: Custom key patterns to detect (optional)
        entropy_threshold: Minimum entropy for potential secrets
        model: DSPy model to use for the guardrail

    Returns:
        Configured SecretKeysGuardrail instance
    """
    config = SecretKeysGuardrailConfig(
        key_patterns=key_patterns,
        entropy_threshold=entropy_threshold,
        model=model,
    )
    return SecretKeysGuardrail(config)


def create_comprehensive_guardrail_suite(
    business_scopes: List[str],
    competitor_names: Optional[List[str]] = None,
    blocked_keywords: Optional[List[str]] = None,
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025",
):
    """Create a comprehensive suite of guardrails for content moderation.

    This factory function creates a GuardrailManager with a full set of guardrails
    configured for typical content moderation needs.

    Args:
        business_scopes: Business topics for topic guardrail
        competitor_names: Competitor names for topic guardrail (optional)
        blocked_keywords: Keywords to block (optional)
        model: DSPy model to use for all guardrails

    Returns:
        GuardrailManager with comprehensive guardrail suite

    Example:
        manager = create_comprehensive_guardrail_suite(
            business_scopes=["AI", "Machine Learning"],
            competitor_names=["OpenAI", "Google"],
            blocked_keywords=["inappropriate", "offensive"]
        )
        results = manager.check("User content to moderate")
    """
    from dspy_guardrails.core.manager import GuardrailManager

    manager = GuardrailManager()

    # Add topic guardrail
    if competitor_names is None:
        competitor_names = []
    topic_config = TopicGuardrailConfig(
        business_scopes=business_scopes,
        competitor_names=competitor_names,
        model=model,
    )
    manager.add_guardrail("topic", TopicGuardrail(topic_config))

    # Add NSFW guardrail
    nsfw_config = NsfwGuardrailConfig(model=model)
    manager.add_guardrail("nsfw", NsfwGuardrail(nsfw_config))

    # Add jailbreak guardrail
    jailbreak_config = JailbreakGuardrailConfig(model=model)
    manager.add_guardrail("jailbreak", JailbreakGuardrail(jailbreak_config))

    # Add PII guardrail
    pii_config = PiiGuardrailConfig(model=model)
    manager.add_guardrail("pii", PiiGuardrail(pii_config))

    # Add prompt injection guardrail
    injection_config = PromptInjectionGuardrailConfig(model=model)
    manager.add_guardrail(
        "prompt_injection", PromptInjectionGuardrail(injection_config)
    )

    # Add keywords guardrail if keywords provided
    if blocked_keywords:
        keywords_config = KeywordsGuardrailConfig(
            blocked_keywords=blocked_keywords,
            model=model,
        )
        manager.add_guardrail("keywords", KeywordsGuardrail(keywords_config))

    # Add secret keys guardrail
    secret_config = SecretKeysGuardrailConfig(model=model)
    manager.add_guardrail("secret_keys", SecretKeysGuardrail(secret_config))

    return manager
