"""Guardrail creation functions with method-based API."""

from typing import List, Optional, Union

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import (
    JailbreakGuardrailConfig,
    KeywordsGuardrailConfig,
    NsfwGuardrailConfig,
    PiiGuardrailConfig,
    PromptInjectionGuardrailConfig,
    SecretKeysGuardrailConfig,
    TopicGuardrailConfig,
)
from dspy_guardrails.core.config import configure as _configure
from dspy_guardrails.guardrails import (
    JailbreakGuardrail,
    KeywordsGuardrail,
    NsfwGuardrail,
    PiiGuardrail,
    PromptInjectionGuardrail,
    SecretKeysGuardrail,
    TopicGuardrail,
)


def configure(lm=None, **kwargs):
    """
    Configure DSPy globally for guardrail usage.

    This function sets up DSPy configuration that will be used by all guardrails.
    It should be called once at application startup before creating any guardrails.

    Args:
        lm: DSPy language model to use for guardrails
        **kwargs: Additional configuration options

    Example:
        import dspy
        from dspy_guardrails import guardrail

        lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="key")
        guardrail.configure(lm=lm)
    """
    return _configure(lm=lm, **kwargs)


def topic(
    business_scopes: List[str],
    competitor_names: Optional[List[str]] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> TopicGuardrail:
    """
    Create a topic compliance guardrail.

    Args:
        business_scopes: List of business topics that are considered on-topic
        competitor_names: List of competitor names to flag (optional)
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured TopicGuardrail instance

    Example:
        guardrail = topic(
            business_scopes=["AI", "Machine Learning"],
            competitor_names=["OpenAI", "Google"]
        )
    """
    if competitor_names is None:
        competitor_names = []

    config = TopicGuardrailConfig(
        business_scopes=business_scopes,
        competitor_names=competitor_names,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return TopicGuardrail(config)


def nsfw(
    sensitivity_level: str = "medium",
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> NsfwGuardrail:
    """
    Create an NSFW content detection guardrail.

    Args:
        sensitivity_level: Sensitivity level ("low", "medium", "high")
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured NsfwGuardrail instance

    Example:
        guardrail = nsfw(sensitivity_level="high")
    """
    config = NsfwGuardrailConfig(
        sensitivity_level=sensitivity_level,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return NsfwGuardrail(config)


def jailbreak(
    detection_threshold: float = 0.8,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> JailbreakGuardrail:
    """
    Create a jailbreak detection guardrail.

    Args:
        detection_threshold: Confidence threshold for flagging jailbreaks (0.0-1.0)
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured JailbreakGuardrail instance

    Example:
        guardrail = jailbreak(detection_threshold=0.9)
    """
    config = JailbreakGuardrailConfig(
        detection_threshold=detection_threshold,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return JailbreakGuardrail(config)


def pii(
    allowed_pii_types: Optional[List[str]] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> PiiGuardrail:
    """
    Create a PII detection guardrail.

    Args:
        allowed_pii_types: List of PII types that are allowed (None means all PII blocked)
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured PiiGuardrail instance

    Example:
        guardrail = pii(allowed_pii_types=["email"])
    """
    config = PiiGuardrailConfig(
        allowed_pii_types=allowed_pii_types,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return PiiGuardrail(config)


def prompt_injection(
    injection_patterns: Optional[List[str]] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> PromptInjectionGuardrail:
    """
    Create a prompt injection detection guardrail.

    Args:
        injection_patterns: Custom injection patterns to detect (optional)
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured PromptInjectionGuardrail instance

    Example:
        guardrail = prompt_injection()
    """
    config = PromptInjectionGuardrailConfig(
        injection_patterns=injection_patterns,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return PromptInjectionGuardrail(config)


def keywords(
    blocked_keywords: List[str],
    case_sensitive: bool = False,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> KeywordsGuardrail:
    """
    Create a keyword filtering guardrail.

    Args:
        blocked_keywords: List of keywords to block
        case_sensitive: Whether keyword matching is case sensitive
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured KeywordsGuardrail instance

    Example:
        guardrail = keywords(blocked_keywords=["inappropriate", "offensive"])
    """
    config = KeywordsGuardrailConfig(
        blocked_keywords=blocked_keywords,
        case_sensitive=case_sensitive,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return KeywordsGuardrail(config)


def secret_keys(
    key_patterns: Optional[List[str]] = None,
    entropy_threshold: float = 4.0,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> SecretKeysGuardrail:
    """
    Create a secret keys detection guardrail.

    Args:
        key_patterns: Custom key patterns to detect (optional)
        entropy_threshold: Minimum entropy for potential secrets
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured SecretKeysGuardrail instance

    Example:
        guardrail = secret_keys(entropy_threshold=3.5)
    """
    config = SecretKeysGuardrailConfig(
        key_patterns=key_patterns,
        entropy_threshold=entropy_threshold,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return SecretKeysGuardrail(config)


def Run(
    guardrails: Union[BaseGuardrail, List[BaseGuardrail]],
    text: str,
    early_return: bool = False,
) -> Union[GuardrailResult, List[GuardrailResult]]:
    """
    Execute guardrail(s) on input text with configurable behavior.

    Args:
        guardrails: Single guardrail or list of guardrails to execute
        text: Input text to check against guardrails
        early_return: If True, stop execution on first failure. If False (default), run all guardrails.

    Returns:
        Single GuardrailResult for single guardrail, or List[GuardrailResult] for multiple guardrails

    Examples:
        # Single guardrail
        result = guardrail.Run(topic_guardrail, "some text")

        # Multiple guardrails, run all (default)
        results = guardrail.Run([topic_gr, nsfw_gr], "some text")

        # Multiple guardrails with early return on failure
        results = guardrail.Run([topic_gr, nsfw_gr], "some text", early_return=True)
    """
    # Handle single guardrail case
    if isinstance(guardrails, BaseGuardrail):
        return guardrails.check(text)

    # Handle list of guardrails case
    if not isinstance(guardrails, list):
        raise TypeError(
            "guardrails must be a BaseGuardrail instance or list of BaseGuardrail instances"
        )

    results = []
    for guardrail in guardrails:
        if not isinstance(guardrail, BaseGuardrail):
            raise TypeError(
                "All items in guardrails list must be BaseGuardrail instances"
            )

        result = guardrail.check(text)
        results.append(result)

        # Early return if requested and guardrail failed
        if early_return and not result.is_allowed:
            break

    return results
