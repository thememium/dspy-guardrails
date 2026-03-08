"""Guardrail creation classes with method-based API."""

from typing import List, Optional, Sequence, Union

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import (
    GibberishGuardrailConfig,
    GroundingGuardrailConfig,
    JailbreakGuardrailConfig,
    KeywordsGuardrailConfig,
    LanguageGuardrailConfig,
    NsfwGuardrailConfig,
    PiiGuardrailConfig,
    PromptInjectionGuardrailConfig,
    SecretKeysGuardrailConfig,
    ToneGuardrailConfig,
    TopicGuardrailConfig,
    ToxicityGuardrailConfig,
)
from dspy_guardrails.core.config import configure as _configure
from dspy_guardrails.guardrails import (
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


def Topic(
    topic_scopes: List[str],
    blocked_topics: Optional[List[str]] = None,
) -> TopicGuardrail:
    """
    Create a topic compliance guardrail.

    Args:
        topic_scopes: List of topic scopes that are considered on-topic
        blocked_topics: List of blocked topics or items to flag (optional)

    Returns:
        Configured TopicGuardrail instance

    Example:
        guardrail = Topic(
            topic_scopes=["AI", "Machine Learning"],
            blocked_topics=["OpenAI", "Google"]
        )
    """
    if blocked_topics is None:
        blocked_topics = []

    config = TopicGuardrailConfig(
        topic_scopes=topic_scopes,
        blocked_topics=blocked_topics,
    )
    return TopicGuardrail(config)


def Nsfw(
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


def Jailbreak(
    detection_threshold: float = 0.8,
) -> JailbreakGuardrail:
    """
    Create a jailbreak detection guardrail.

    Args:
        detection_threshold: Confidence threshold for flagging jailbreaks (0.0-1.0)

    Returns:
        Configured JailbreakGuardrail instance

    Example:
        guardrail = Jailbreak(detection_threshold=0.9)
    """
    config = JailbreakGuardrailConfig(
        detection_threshold=detection_threshold,
    )
    return JailbreakGuardrail(config)


def Pii(
    allowed_pii_types: Optional[List[str]] = None,
) -> PiiGuardrail:
    """
    Create a PII detection guardrail.

    Args:
        allowed_pii_types: List of PII types that are allowed (None means all PII blocked)

    Returns:
        Configured PiiGuardrail instance

    Example:
        guardrail = Pii(allowed_pii_types=["email"])
    """
    config = PiiGuardrailConfig(
        allowed_pii_types=allowed_pii_types,
    )
    return PiiGuardrail(config)


def PromptInjection(
    injection_patterns: Optional[List[str]] = None,
) -> PromptInjectionGuardrail:
    """
    Create a prompt injection detection guardrail.

    Args:
        injection_patterns: Custom injection patterns to detect (optional)

    Returns:
        Configured PromptInjectionGuardrail instance

    Example:
        guardrail = PromptInjection()
    """
    config = PromptInjectionGuardrailConfig(
        injection_patterns=injection_patterns,
    )
    return PromptInjectionGuardrail(config)


def Keywords(
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
        guardrail = Keywords(blocked_keywords=["inappropriate", "offensive"])
    """
    config = KeywordsGuardrailConfig(
        blocked_keywords=blocked_keywords,
        case_sensitive=case_sensitive,
    )
    return KeywordsGuardrail(config)


def SecretKeys(
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
        guardrail = SecretKeys(entropy_threshold=3.5)
    """
    config = SecretKeysGuardrailConfig(
        key_patterns=key_patterns,
        entropy_threshold=entropy_threshold,
    )
    return SecretKeysGuardrail(config)


def Toxicity(
    toxicity_threshold: float = 0.5,
) -> ToxicityGuardrail:
    """
    Create a toxicity detection guardrail.

    Args:
        toxicity_threshold: Confidence threshold for flagging toxicity (0.0-1.0)

    Returns:
        Configured ToxicityGuardrail instance

    Example:
        guardrail = Toxicity(toxicity_threshold=0.7)
    """
    config = ToxicityGuardrailConfig(
        toxicity_threshold=toxicity_threshold,
    )
    return ToxicityGuardrail(config)


def Gibberish(
    prob_threshold: float = 0.5,
) -> GibberishGuardrail:
    """
    Create a gibberish detection guardrail.

    Args:
        prob_threshold: Confidence threshold for flagging gibberish (0.0-1.0)

    Returns:
        Configured GibberishGuardrail instance

    Example:
        guardrail = Gibberish(prob_threshold=0.8)
    """
    config = GibberishGuardrailConfig(
        prob_threshold=prob_threshold,
    )
    return GibberishGuardrail(config)


def Language(
    allowed_languages: List[str],
) -> LanguageGuardrail:
    """
    Create a language detection guardrail.

    Args:
        allowed_languages: List of ISO language codes (e.g., ["en", "es"])

    Returns:
        Configured LanguageGuardrail instance

    Example:
        guardrail = Language(allowed_languages=["en", "fr"])
    """
    config = LanguageGuardrailConfig(
        allowed_languages=allowed_languages,
    )
    return LanguageGuardrail(config)


def Tone(
    desired_tone: str = "polite",
    unwanted_tones: Optional[List[str]] = None,
) -> ToneGuardrail:
    """
    Create a tone/sentiment guardrail.

    Args:
        desired_tone: The desired tone (e.g., "polite")
        unwanted_tones: List of unwanted tones (optional)

    Returns:
        Configured ToneGuardrail instance

    Example:
        guardrail = Tone(desired_tone="helpful", unwanted_tones=["sarcastic"])
    """
    config = ToneGuardrailConfig(
        desired_tone=desired_tone,
        unwanted_tones=unwanted_tones,
    )
    return ToneGuardrail(config)


def Grounding(
    grounding_threshold: float = 0.7,
) -> GroundingGuardrail:
    """
    Create a grounding/hallucination guardrail.

    Args:
        grounding_threshold: Confidence threshold for grounding (0.0-1.0)

    Returns:
        Configured GroundingGuardrail instance

    Example:
        guardrail = Grounding(grounding_threshold=0.8)
    """
    config = GroundingGuardrailConfig(
        grounding_threshold=grounding_threshold,
    )
    return GroundingGuardrail(config)


def Run(
    guardrails: Union[BaseGuardrail, Sequence[BaseGuardrail]],
    text: Union[str, List[str]],
    early_return: bool = False,
    **kwargs,
) -> GuardrailResult:
    """
    Execute guardrail(s) on input text(s) with configurable behavior.

    Args:
        guardrails: Single guardrail or sequence of guardrails to execute
        text: Input text (str) or list of texts (List[str]) to check against guardrails
        early_return: If True, stop execution on first failure. If False (default), run all guardrails.
        **kwargs: Additional parameters passed to each guardrail's check() method (e.g., context="...")

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
    elif isinstance(guardrails, Sequence):
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
            "guardrails must be a BaseGuardrail instance or sequence of BaseGuardrail instances"
        )

    if not isinstance(text, (str, list)):
        raise TypeError("text must be a string or list of strings")

    # Handle cases that should return aggregated results
    if isinstance(text, list) or isinstance(guardrails, Sequence):
        return _run_aggregated(guardrails, text, early_return, **kwargs)

    # Handle single guardrail, single text case
    return guardrails.check(text, **kwargs)


def _run_aggregated(
    guardrails: Union[BaseGuardrail, Sequence[BaseGuardrail]],
    text: Union[str, List[str]],
    early_return: bool = False,
    **kwargs,
) -> GuardrailResult:
    """Handle aggregated processing for multiple guardrails and/or multiple texts."""
    # Normalize inputs
    if isinstance(guardrails, BaseGuardrail):
        guardrail_list = [guardrails]
    elif isinstance(guardrails, Sequence):
        guardrail_list = list(guardrails)
        # Validate all items are BaseGuardrail instances
        for guardrail in guardrail_list:
            if not isinstance(guardrail, BaseGuardrail):
                raise TypeError(
                    "All items in guardrails list must be BaseGuardrail instances"
                )
    else:
        raise TypeError(
            "guardrails must be a BaseGuardrail instance or sequence of BaseGuardrail instances"
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
            result = guardrail.check(text_item, **kwargs)
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
