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
) -> TopicGuardrail:
    """
    Create a topic compliance guardrail.

    Args:
        business_scopes: List of business topics that are considered on-topic
        competitor_names: List of competitor names to flag (optional)

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
    )
    return TopicGuardrail(config)


def nsfw(
    sensitivity_level: str = "medium",
) -> NsfwGuardrail:
    """
    Create an NSFW content detection guardrail.

    Args:
        sensitivity_level: Sensitivity level ("low", "medium", "high")

    Returns:
        Configured NsfwGuardrail instance
    """
    config = NsfwGuardrailConfig(
        sensitivity_level=sensitivity_level,
    )
    return NsfwGuardrail(config)


def jailbreak(
    detection_threshold: float = 0.8,
) -> JailbreakGuardrail:
    """
    Create a jailbreak detection guardrail.

    Args:
        detection_threshold: Confidence threshold for flagging jailbreaks (0.0-1.0)

    Returns:
        Configured JailbreakGuardrail instance

    Example:
        guardrail = jailbreak(detection_threshold=0.9)
    """
    config = JailbreakGuardrailConfig(
        detection_threshold=detection_threshold,
    )
    return JailbreakGuardrail(config)


def pii(
    allowed_pii_types: Optional[List[str]] = None,
) -> PiiGuardrail:
    """
    Create a PII detection guardrail.

    Args:
        allowed_pii_types: List of PII types that are allowed (None means all PII blocked)

    Returns:
        Configured PiiGuardrail instance

    Example:
        guardrail = pii(allowed_pii_types=["email"])
    """
    config = PiiGuardrailConfig(
        allowed_pii_types=allowed_pii_types,
    )
    return PiiGuardrail(config)


def prompt_injection(
    injection_patterns: Optional[List[str]] = None,
) -> PromptInjectionGuardrail:
    """
    Create a prompt injection detection guardrail.

    Args:
        injection_patterns: Custom injection patterns to detect (optional)

    Returns:
        Configured PromptInjectionGuardrail instance

    Example:
        guardrail = prompt_injection()
    """
    config = PromptInjectionGuardrailConfig(
        injection_patterns=injection_patterns,
    )
    return PromptInjectionGuardrail(config)


def keywords(
    blocked_keywords: List[str],
    case_sensitive: bool = False,
) -> KeywordsGuardrail:
    """
    Create a keyword filtering guardrail.

    Args:
        blocked_keywords: List of keywords to block
        case_sensitive: Whether keyword matching is case sensitive

    Returns:
        Configured KeywordsGuardrail instance

    Example:
        guardrail = keywords(blocked_keywords=["inappropriate", "offensive"])
    """
    config = KeywordsGuardrailConfig(
        blocked_keywords=blocked_keywords,
        case_sensitive=case_sensitive,
    )
    return KeywordsGuardrail(config)


def secret_keys(
    key_patterns: Optional[List[str]] = None,
    entropy_threshold: float = 4.0,
) -> SecretKeysGuardrail:
    """
    Create a secret keys detection guardrail.

    Args:
        key_patterns: Custom key patterns to detect (optional)
        entropy_threshold: Minimum entropy for potential secrets

    Returns:
        Configured SecretKeysGuardrail instance

    Example:
        guardrail = secret_keys(entropy_threshold=3.5)
    """
    config = SecretKeysGuardrailConfig(
        key_patterns=key_patterns,
        entropy_threshold=entropy_threshold,
    )
    return SecretKeysGuardrail(config)


def Run(
    guardrails: Union[BaseGuardrail, List[BaseGuardrail]],
    text: Union[str, List[str]],
    early_return: bool = False,
) -> GuardrailResult:
    """
    Execute guardrail(s) on input text(s) with configurable behavior.

    Args:
        guardrails: Single guardrail or list of guardrails to execute
        text: Input text (str) or list of texts (List[str]) to check against guardrails
        early_return: If True, stop execution on first failure. If False (default), run all guardrails.

    Returns:
        Single GuardrailResult when single guardrail is used, or aggregated GuardrailResult
        when multiple guardrails or multiple texts are provided

    Examples:
        # Single guardrail, single text (returns single result)
        result = guardrail.Run(topic_guardrail, "some text")

        # Multiple guardrails, single text (returns aggregated result)
        result = guardrail.Run([topic_gr, nsfw_gr], "some text")

        # Single guardrail, multiple texts (returns aggregated result)
        result = guardrail.Run(topic_guardrail, ["text1", "text2", "text3"])

        # Multiple guardrails, multiple texts (returns aggregated result)
        result = guardrail.Run([topic_gr, nsfw_gr], ["text1", "text2"], early_return=True)
    """
    # Validate inputs
    if isinstance(guardrails, BaseGuardrail):
        pass  # Valid single guardrail
    elif isinstance(guardrails, list):
        if not guardrails:
            pass  # Empty list is allowed
        else:
            for gr in guardrails:
                if not isinstance(gr, BaseGuardrail):
                    raise TypeError(
                        "All items in guardrails list must be BaseGuardrail instances"
                    )
    else:
        raise TypeError(
            "guardrails must be a BaseGuardrail instance or list of BaseGuardrail instances"
        )

    if not isinstance(text, (str, list)):
        raise TypeError("text must be a string or list of strings")

    # Handle cases that should return aggregated results
    if isinstance(text, list) or isinstance(guardrails, list):
        return _run_aggregated(guardrails, text, early_return)

    # Handle single guardrail, single text case
    return guardrails.check(text)


def _run_aggregated(
    guardrails: Union[BaseGuardrail, List[BaseGuardrail]],
    text: Union[str, List[str]],
    early_return: bool = False,
) -> GuardrailResult:
    """Handle aggregated processing for multiple guardrails and/or multiple texts."""
    # Normalize inputs
    if isinstance(guardrails, BaseGuardrail):
        guardrail_list = [guardrails]
    elif isinstance(guardrails, list):
        guardrail_list = guardrails
        # Validate all items are BaseGuardrail instances
        for guardrail in guardrail_list:
            if not isinstance(guardrail, BaseGuardrail):
                raise TypeError(
                    "All items in guardrails list must be BaseGuardrail instances"
                )
    else:
        raise TypeError(
            "guardrails must be a BaseGuardrail instance or list of BaseGuardrail instances"
        )

    if isinstance(text, str):
        text_list = [text]
    elif isinstance(text, list):
        text_list = text
    else:
        raise TypeError("text must be a string or list of strings")

    all_results = []
    global_allowed = True
    first_failure_reason = None

    # Process each text against all guardrails
    for text_index, text_item in enumerate(text_list):
        text_results = []

        for guardrail in guardrail_list:
            result = guardrail.check(text_item)
            text_results.append(result)

            # Track global state
            if not result.is_allowed:
                global_allowed = False
                if first_failure_reason is None:
                    first_failure_reason = (
                        result.reason or f"Failed {guardrail.name} check"
                    )

            # Early return if requested and any guardrail failed for this text
            if early_return and not result.is_allowed:
                break

        all_results.append(
            {"text_index": text_index, "text": text_item, "results": text_results}
        )

        # If early return and this text failed, stop processing further texts
        if early_return and not all(r.is_allowed for r in text_results):
            break

    # Create aggregated result
    guardrail_names = [gr.name for gr in guardrail_list]
    aggregated_result = GuardrailResult(
        is_allowed=global_allowed,
        reason=first_failure_reason,
        metadata={
            "text_results": all_results,
            "guardrail_names": guardrail_names,
            "total_texts": len(text_list),
            "processed_texts": len(all_results),
        },
        guardrail_name="aggregated",
    )

    return aggregated_result
