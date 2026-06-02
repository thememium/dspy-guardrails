"""Guardrail creation classes with method-based API."""

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Sequence, Union

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
    enable_blocked_topic_prefilter: bool = True,
) -> TopicGuardrail:
    """
    Create a topic compliance guardrail.

    Args:
        topic_scopes: List of topic scopes that are considered on-topic
        blocked_topics: List of blocked topics or items to flag (optional)
        enable_blocked_topic_prefilter: When True, run a substring
            prefilter against ``blocked_topics`` before the DSPy LLM
            call. The prefilter is partial - it cannot evaluate
            ``topic_scopes`` (which requires semantic understanding)
            so the LLM still runs when no blocked topic is found.

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
        enable_blocked_topic_prefilter=enable_blocked_topic_prefilter,
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
    enable_regex_prefilter: bool = True,
) -> JailbreakGuardrail:
    """
    Create a jailbreak detection guardrail.

    Args:
        detection_threshold: Confidence threshold for flagging jailbreaks (0.0-1.0)
        enable_regex_prefilter: When True, run the built-in jailbreak
            catalog (DAN/AIM/AntiGPT, role-play bypass templates,
            hypothetical-unrestricted framing, etc.) before the DSPy
            LLM call.

    Returns:
        Configured JailbreakGuardrail instance

    Example:
        guardrail = Jailbreak(detection_threshold=0.9)
    """
    config = JailbreakGuardrailConfig(
        detection_threshold=detection_threshold,
        enable_regex_prefilter=enable_regex_prefilter,
    )
    return JailbreakGuardrail(config)


def Pii(
    allowed_pii_types: Optional[List[str]] = None,
    enable_regex_prefilter: bool = True,
    pii_actions: Optional[Dict[str, str]] = None,
    custom_patterns: Optional[List[Dict]] = None,
) -> PiiGuardrail:
    """
    Create a PII detection guardrail.

    Args:
        allowed_pii_types: List of PII types that are allowed (None means
            all PII blocked). Legacy escape-hatch - removes types from
            the regex prefilter entirely.
        enable_regex_prefilter: When True, run the built-in regex
            prefilter (email / phone / SSN / credit-card / IP-address
            presets plus any custom patterns) before the DSPy LLM call.
        pii_actions: Per-preset action override. Maps slug to either
            ``"redact"`` (replace with labeled placeholder, request
            continues) or ``"block"`` (request is rejected).
        custom_patterns: User-supplied regex patterns. Each entry is a
            dict with ``name``, ``pattern``, ``action`` (``"redact"`` or
            ``"block"``), and optional ``label``.

    Returns:
        Configured PiiGuardrail instance

    Examples:
        guardrail = Pii(allowed_pii_types=["email"])

        guardrail = Pii(
            pii_actions={"email": "redact", "ssn": "block"},
            custom_patterns=[
                {
                    "name": "aws_key",
                    "pattern": r"AKIA[0-9A-Z]{16}",
                    "action": "block",
                    "label": "AWS Key",
                }
            ],
        )
    """
    config = PiiGuardrailConfig(
        allowed_pii_types=allowed_pii_types,
        enable_regex_prefilter=enable_regex_prefilter,
        pii_actions=pii_actions,
        custom_patterns=custom_patterns,
    )
    return PiiGuardrail(config)


def PromptInjection(
    injection_patterns: Optional[List[str]] = None,
    enable_regex_prefilter: bool = True,
    custom_regex_patterns: Optional[dict] = None,
) -> PromptInjectionGuardrail:
    """
    Create a prompt injection detection guardrail.

    Args:
        injection_patterns: Custom injection patterns (passed through to
            the GuardrailResult metadata; not used for matching by default,
            retained for backward compatibility).
        enable_regex_prefilter: When True, run the built-in regex
            prefilter (pattern catalog + typoglycemia / Base64 / hex /
            whitespace-evasion detectors) before the DSPy LLM call.
        custom_regex_patterns: Optional dict of ``{name: regex}`` patterns
            added to the built-in prefilter defaults.

    Returns:
        Configured PromptInjectionGuardrail instance

    Example:
        guardrail = PromptInjection()
    """
    config = PromptInjectionGuardrailConfig(
        injection_patterns=injection_patterns,
        enable_regex_prefilter=enable_regex_prefilter,
        custom_regex_patterns=custom_regex_patterns,
    )
    return PromptInjectionGuardrail(config)


def Keywords(
    blocked_keywords: List[str],
    case_sensitive: bool = False,
    enable_regex_prefilter: bool = True,
    word_boundary: bool = True,
    use_wildcards: bool = False,
) -> KeywordsGuardrail:
    """
    Create a keyword filtering guardrail.

    Args:
        blocked_keywords: List of keywords to block
        case_sensitive: Whether keyword matching is case sensitive
        enable_regex_prefilter: When True, run the compiled-keyword
            prefilter before the DSPy LLM call.
        word_boundary: When True, multi-word keywords are wrapped in
            ``\\b`` so ``"spam"`` does not match ``"spamming"``.
        use_wildcards: When True, ``*`` and ``?`` in keywords are
            translated to ``.*`` and ``.``.

    Returns:
        Configured KeywordsGuardrail instance

    Example:
        guardrail = Keywords(blocked_keywords=["inappropriate", "offensive"])
    """
    config = KeywordsGuardrailConfig(
        blocked_keywords=blocked_keywords,
        case_sensitive=case_sensitive,
        enable_regex_prefilter=enable_regex_prefilter,
        word_boundary=word_boundary,
        use_wildcards=use_wildcards,
    )
    return KeywordsGuardrail(config)


def SecretKeys(
    key_patterns: Optional[List[str]] = None,
    entropy_threshold: float = 4.0,
    enable_regex_prefilter: bool = True,
    custom_patterns: Optional[List[Dict]] = None,
) -> SecretKeysGuardrail:
    """
    Create a secret keys detection guardrail.

    Args:
        key_patterns: Custom key patterns to detect (optional)
        entropy_threshold: Minimum entropy for potential secrets
        enable_regex_prefilter: When True, run the built-in provider
            catalog (OpenAI, GitHub, AWS, Google, Stripe, Slack, JWT,
            PEM private keys, etc.) plus any custom patterns before
            the DSPy LLM call.
        custom_patterns: User-supplied regex patterns. Each entry is
            a dict with ``name``, ``pattern``, and optional ``label``.

    Returns:
        Configured SecretKeysGuardrail instance

    Example:
        guardrail = SecretKeys(entropy_threshold=3.5)
    """
    config = SecretKeysGuardrailConfig(
        key_patterns=key_patterns,
        entropy_threshold=entropy_threshold,
        enable_regex_prefilter=enable_regex_prefilter,
        custom_patterns=custom_patterns,
    )
    return SecretKeysGuardrail(config)


def Toxicity(
    toxicity_threshold: float = 0.5,
    enable_regex_prefilter: bool = True,
) -> ToxicityGuardrail:
    """
    Create a toxicity detection guardrail.

    Args:
        toxicity_threshold: Confidence threshold for flagging toxicity (0.0-1.0)
        enable_regex_prefilter: When True, run the curated high-precision
            profanity/threat catalog before the DSPy LLM call. The
            catalog is conservative (low recall, very high precision);
            disable if false-positive cost is unacceptable.

    Returns:
        Configured ToxicityGuardrail instance

    Example:
        guardrail = Toxicity(toxicity_threshold=0.7)
    """
    config = ToxicityGuardrailConfig(
        toxicity_threshold=toxicity_threshold,
        enable_regex_prefilter=enable_regex_prefilter,
    )
    return ToxicityGuardrail(config)


def Gibberish(
    prob_threshold: float = 0.5,
    enable_regex_prefilter: bool = True,
) -> GibberishGuardrail:
    """
    Create a gibberish detection guardrail.

    Args:
        prob_threshold: Confidence threshold for flagging gibberish (0.0-1.0)
        enable_regex_prefilter: When True, run the surface-feature
            prefilter (keyboard mashes, repeated characters, etc.)
            before the DSPy LLM call.

    Returns:
        Configured GibberishGuardrail instance

    Example:
        guardrail = Gibberish(prob_threshold=0.8)
    """
    config = GibberishGuardrailConfig(
        prob_threshold=prob_threshold,
        enable_regex_prefilter=enable_regex_prefilter,
    )
    return GibberishGuardrail(config)


def Language(
    allowed_languages: List[str],
    enable_script_prefilter: bool = True,
) -> LanguageGuardrail:
    """
    Create a language detection guardrail.

    Args:
        allowed_languages: List of ISO language codes (e.g., ["en", "es"])
        enable_script_prefilter: When True, run a fast Unicode-script
            prefilter (CJK, Cyrillic, Arabic, etc.) that short-circuits
            requests whose dominant script is unambiguously outside
            ``allowed_languages``. Latin-script input still falls
            through to the LLM.

    Returns:
        Configured LanguageGuardrail instance

    Example:
        guardrail = Language(allowed_languages=["en", "fr"])
    """
    config = LanguageGuardrailConfig(
        allowed_languages=allowed_languages,
        enable_script_prefilter=enable_script_prefilter,
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
    parallel: bool = False,
    num_threads: Optional[int] = None,
    **kwargs,
) -> GuardrailResult:
    """
    Execute guardrail(s) on input text(s) with configurable behavior.

    Args:
        guardrails: Single guardrail or sequence of guardrails to execute
        text: Input text (str) or list of texts (List[str]) to check against guardrails
        early_return: If True, stop execution on first failure. If False (default), run all guardrails.
        parallel: If True, run guardrails concurrently using a
            ``ThreadPoolExecutor`` (one task per guardrail per text).
            Has no effect on the single-guardrail/single-text fast
            path. When combined with ``early_return=True``, all
            guardrails still execute (they run concurrently) but the
            result reflects the first failure.
        num_threads: Optional override for the parallel thread pool
            size. Defaults to ``min(len(guardrails), 32)`` (Python's
            default) when ``None``.
        **kwargs: Additional parameters passed to each guardrail's check() method (e.g., context="...")

    Returns:
        Single GuardrailResult when single guardrail is used, or aggregated GuardrailResult
        when multiple guardrails or multiple texts are provided

    Examples:
        # Single guardrail, single text (returns single result)
        result = guardrail.Run(topic_guardrail, "some text")

        # Multiple guardrails, single text (returns aggregated result)
        result = guardrail.Run([topic_gr, nsfw_gr], "some text")

        # Multiple guardrails, run concurrently
        result = guardrail.Run(
            [topic_gr, pii_gr, secret_keys_gr],
            "Email me at user@example.com",
            parallel=True,
        )

        # Single guardrail, multiple texts (returns aggregated result)
        result = guardrail.Run(topic_guardrail, ["text1", "text2", "text3"])

        # Multiple guardrails, multiple texts (returns aggregated result)
        result = guardrail.Run(
            [topic_gr, nsfw_gr], ["text1", "text2"], early_return=True
        )
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
        return _run_aggregated(
            guardrails,
            text,
            early_return,
            parallel=parallel,
            num_threads=num_threads,
            **kwargs,
        )

    # Handle single guardrail, single text case
    return guardrails.check(text, **kwargs)


def _run_aggregated(
    guardrails: Union[BaseGuardrail, Sequence[BaseGuardrail]],
    text: Union[str, List[str]],
    early_return: bool = False,
    parallel: bool = False,
    num_threads: Optional[int] = None,
    **kwargs,
) -> GuardrailResult:
    """Run guardrails per text, optionally concurrently via a thread pool.

    When ``parallel=True`` and there are 2+ guardrails, each text's
    guardrail fan-out is executed concurrently on a
    ``ThreadPoolExecutor`` (one task per guardrail). With
    ``early_return=True``, guardrails within a text still all execute
    (they run concurrently), but processing stops at the first text
    that has any failure.
    """
    # Normalize inputs
    if isinstance(guardrails, BaseGuardrail):
        guardrail_list = [guardrails]
    elif isinstance(guardrails, Sequence):
        guardrail_list = list(guardrails)
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

    use_parallel = parallel and len(guardrail_list) > 1

    for text_index, text_item in enumerate(text_list):
        if use_parallel:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [
                    executor.submit(gr.check, text_item, **kwargs)
                    for gr in guardrail_list
                ]
                text_results = [f.result() for f in futures]
        else:
            text_results = []
            for guardrail in guardrail_list:
                result = guardrail.check(text_item, **kwargs)
                text_results.append(result)
                if early_return and not result.is_allowed:
                    break

        for guardrail, result in zip(guardrail_list, text_results):
            if not result.is_allowed:
                global_allowed = False
                if first_failure_reason is None:
                    first_failure_reason = (
                        result.reason or f"Failed {guardrail.name} check"
                    )

        all_results.append(
            {
                "text_index": text_index,
                "text": text_item,
                "results": text_results,
            }
        )

        if early_return and not all(r.is_allowed for r in text_results):
            break

    guardrail_names = [gr.name for gr in guardrail_list]
    aggregated_result = GuardrailResult(
        is_allowed=global_allowed,
        reason=first_failure_reason,
        metadata={
            "text_results": all_results,
            "guardrail_names": guardrail_names,
            "total_texts": len(text_list),
            "processed_texts": len(all_results),
            "parallel": use_parallel,
            "num_threads": num_threads if use_parallel else None,
        },
        guardrail_name="aggregated",
    )

    return aggregated_result
