"""Configuration classes for DSPy Guardrails."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GuardrailConfig:
    """Base configuration class for all guardrails.

    This class provides common configuration options that apply to all guardrails.
    Specific guardrails can extend this class with their own configuration options.
    """

    # DSPy configuration is now handled globally - no per-guardrail model config


@dataclass
class TopicGuardrailConfig(GuardrailConfig):
    """Configuration for Topic Compliance Guardrail.

    Attributes:
        topic_scopes: List of topic scopes that are considered on-topic.
        blocked_topics: List of blocked topics or items to flag.
        enable_blocked_topic_prefilter: When True, run a substring
            prefilter against ``blocked_topics`` before the DSPy LLM
            call. The prefilter is partial — it cannot evaluate
            ``topic_scopes`` (which requires semantic understanding)
            so the LLM still runs when no blocked topic is found.
    """

    topic_scopes: Optional[list[str]] = None
    blocked_topics: Optional[list[str]] = None
    enable_blocked_topic_prefilter: bool = True

    def __post_init__(self):
        """Validate topic-specific configuration."""
        if self.topic_scopes is None:
            raise ValueError("topic_scopes is required")
        if self.blocked_topics is None:
            raise ValueError("blocked_topics is required")
        if not self.topic_scopes:
            raise ValueError("topic_scopes cannot be empty")
        # blocked_topics can be empty - it's optional


@dataclass
class NsfwGuardrailConfig(GuardrailConfig):
    """Configuration for NSFW Detection Guardrail."""

    sensitivity_level: str = "medium"  # low, medium, high
    nsfw_content_types: Optional[list[str]] = None

    def __post_init__(self):
        """Validate NSFW-specific configuration."""
        if self.sensitivity_level not in ["low", "medium", "high"]:
            raise ValueError("sensitivity_level must be 'low', 'medium', or 'high'")
        if self.nsfw_content_types is None:
            self.nsfw_content_types = [
                "Sexual content and explicit material",
                "Hate speech and discriminatory language",
                "Harassment and bullying",
                "Violence and gore",
                "Self-harm and suicide references",
                "Profanity and vulgar language",
                "Illegal activities (drugs, theft, weapons, etc.)",
                "Adult themes and mature content",
                "Inappropriate workplace content",
                "Extremist or radical content",
                "Exploitation or abuse",
                "Graphic medical content",
                "Other potentially offensive or inappropriate content",
            ]


@dataclass
class JailbreakGuardrailConfig(GuardrailConfig):
    """Configuration for Jailbreak Detection Guardrail.

    Attributes:
        detection_threshold: Confidence threshold for flagging
            jailbreaks (0.0 to 1.0).
        enable_regex_prefilter: When True, run the built-in jailbreak
            catalog (DAN/AIM/AntiGPT, role-play bypass templates,
            hypothetical-unrestricted framing, etc.) before the DSPy
            LLM call. Disable to force every check through the LLM.
    """

    detection_threshold: float = 0.8  # 0.0 to 1.0
    enable_regex_prefilter: bool = True

    def __post_init__(self):
        """Validate jailbreak-specific configuration."""
        if not (0.0 <= self.detection_threshold <= 1.0):
            raise ValueError("detection_threshold must be between 0.0 and 1.0")


@dataclass
class PiiGuardrailConfig(GuardrailConfig):
    """Configuration for PII Detection Guardrail.

    Attributes:
        allowed_pii_types: Legacy escape-hatch. Any PII type listed here
            is excluded from the regex prefilter entirely. Use
            ``pii_actions`` to selectively block or redact instead.
        enable_regex_prefilter: When True, run the built-in regex
            prefilter (email / phone / SSN / credit-card / IP-address
            presets plus any custom patterns) before the DSPy LLM call.
            Disable to force every check through the LLM.
        pii_actions: Per-preset action override. Maps slug (``"email"``,
            ``"phone"``, ``"ssn"``, ``"credit-card"``, ``"ip-address"``)
            to ``"redact"`` (replace with labeled placeholder, request
            continues) or ``"block"`` (request is rejected with
            ``is_allowed=False``). Unspecified presets default to
            ``"redact"``.
        custom_patterns: User-supplied regex patterns. Each entry is a
            dict with ``name``, ``pattern``, ``action`` (``"redact"`` or
            ``"block"``), and optional ``label`` (defaults to
            ``"[REDACTED]"`` for redact actions, used in the block
            message for block actions). Custom patterns are validated
            for catastrophic backtracking at construction time.
    """

    allowed_pii_types: Optional[list[str]] = None
    enable_regex_prefilter: bool = True
    pii_actions: Optional[dict[str, str]] = None
    custom_patterns: Optional[list[dict]] = None

    def __post_init__(self):
        """Validate PII-specific configuration."""
        if self.allowed_pii_types is None:
            self.allowed_pii_types = []
        if self.pii_actions is None:
            self.pii_actions = {}
        if self.custom_patterns is None:
            self.custom_patterns = []

        # Lazy import to avoid a circular import at module load time.
        from dspy_guardrails.guardrails.pii import PII_PATTERNS, _is_unsafe_pattern

        for slug, action in self.pii_actions.items():
            if action not in ("redact", "block"):
                raise ValueError(
                    f"pii_actions[{slug!r}] must be 'redact' or 'block', got {action!r}"
                )
            if slug not in PII_PATTERNS:
                raise ValueError(
                    f"pii_actions contains unknown slug {slug!r}; "
                    f"valid built-in slugs are {sorted(PII_PATTERNS)}"
                )

        for entry in self.custom_patterns:
            for required in ("name", "pattern", "action"):
                if required not in entry:
                    raise ValueError(
                        f"custom_patterns entry missing required field "
                        f"{required!r}: {entry}"
                    )
            if entry["action"] not in ("redact", "block"):
                raise ValueError(
                    f"custom_patterns[{entry['name']!r}].action must be "
                    f"'redact' or 'block', got {entry['action']!r}"
                )
            if _is_unsafe_pattern(entry["pattern"]):
                raise ValueError(
                    f"custom_patterns[{entry['name']!r}].pattern is "
                    f"rejected: contains nested quantifiers or "
                    f"overlapping alternations that could cause "
                    f"catastrophic backtracking (ReDoS)"
                )


@dataclass
class PromptInjectionGuardrailConfig(GuardrailConfig):
    """Configuration for Prompt Injection Guardrail.

    Attributes:
        injection_patterns: User-supplied substring patterns (passed through
            to the GuardrailResult metadata; not used for matching by
            default, but retained for backward compatibility with the
            documented public API).
        enable_regex_prefilter: When True, run the OpenRouter regex prefilter
            (30+ patterns + typoglycemia / Base64 / hex / whitespace
            evasion detectors) before the DSPy LLM call. Disable to force
            every check through the LLM.
        custom_regex_patterns: Optional dict of ``{name: regex}`` patterns
            that are added (additive, not replacing) to the OpenRouter
            defaults when the prefilter is enabled.
    """

    injection_patterns: Optional[list[str]] = None
    enable_regex_prefilter: bool = True
    custom_regex_patterns: Optional[dict[str, str]] = None

    def __post_init__(self):
        """Validate prompt injection-specific configuration."""
        if self.injection_patterns is None:
            self.injection_patterns = []
        if self.custom_regex_patterns is None:
            self.custom_regex_patterns = {}


@dataclass
class KeywordsGuardrailConfig(GuardrailConfig):
    """Configuration for Keyword Filtering Guardrail.

    Attributes:
        blocked_keywords: Substrings or wildcard patterns to block.
        case_sensitive: Whether matching is case sensitive.
        enable_regex_prefilter: When True, run the compiled-keyword
            prefilter before the DSPy LLM call. Disable to force every
            check through the LLM.
        word_boundary: When True, multi-word keywords are wrapped in
            ``\\b`` so ``"spam"`` does not match ``"spamming"``.
        use_wildcards: When True, ``*`` and ``?`` in keywords are
            translated to ``.*`` and ``.`` respectively.
    """

    blocked_keywords: Optional[list[str]] = None
    case_sensitive: bool = False
    enable_regex_prefilter: bool = True
    word_boundary: bool = True
    use_wildcards: bool = False

    def __post_init__(self):
        """Validate keywords-specific configuration."""
        if self.blocked_keywords is None:
            raise ValueError("blocked_keywords is required")
        if not self.blocked_keywords:
            raise ValueError("blocked_keywords cannot be empty")


@dataclass
class SecretKeysGuardrailConfig(GuardrailConfig):
    """Configuration for Secret Keys Detection Guardrail.

    Attributes:
        key_patterns: User-supplied list of known key prefixes (e.g.,
            ``["sk-", "ghp_"]``) to scan for.
        entropy_threshold: Minimum Shannon entropy (bits/char) for
            high-entropy candidates to be flagged.
        enable_regex_prefilter: When True, run the built-in provider
            catalog (OpenAI, GitHub, AWS, Google, Stripe, Slack, JWT,
            PEM private keys, etc.) plus any custom patterns before
            the DSPy LLM call. Disable to force every check through
            the LLM.
        custom_patterns: User-supplied regex patterns. Each entry is a
            dict with ``name``, ``pattern``, and optional ``label``.
            Custom patterns are ReDoS-screened at construction time.
    """

    key_patterns: Optional[list[str]] = None
    entropy_threshold: float = 4.0
    enable_regex_prefilter: bool = True
    custom_patterns: Optional[list[dict]] = None

    def __post_init__(self):
        """Validate secret keys-specific configuration."""
        if self.key_patterns is None:
            self.key_patterns = []
        if self.entropy_threshold < 0:
            raise ValueError("entropy_threshold must be non-negative")
        if self.custom_patterns is None:
            self.custom_patterns = []


@dataclass
class ToxicityGuardrailConfig(GuardrailConfig):
    """Configuration for Toxicity Detection Guardrail.

    Attributes:
        toxicity_threshold: Confidence threshold for flagging toxicity
            (0.0 to 1.0).
        enable_regex_prefilter: When True, run the curated high-precision
            profanity/threat catalog before the DSPy LLM call. The
            catalog is conservative (low recall, very high precision);
            disable if false-positive cost is unacceptable.
    """

    toxicity_threshold: float = 0.5  # 0.0 to 1.0
    enable_regex_prefilter: bool = True

    def __post_init__(self):
        """Validate toxicity-specific configuration."""
        if not (0.0 <= self.toxicity_threshold <= 1.0):
            raise ValueError("toxicity_threshold must be between 0.0 and 1.0")


@dataclass
class GibberishGuardrailConfig(GuardrailConfig):
    """Configuration for Gibberish Detection Guardrail.

    Attributes:
        prob_threshold: Confidence threshold for flagging gibberish
            (0.0 to 1.0).
        enable_regex_prefilter: When True, run the surface-feature
            prefilter (keyboard mashes, repeated characters, all-
            consonant runs, punctuation spam) plus structural
            heuristics (vowel ratio, no-whitespace long strings)
            before the DSPy LLM call. Disable to force every check
            through the LLM.
    """

    prob_threshold: float = 0.5  # 0.0 to 1.0
    enable_regex_prefilter: bool = True

    def __post_init__(self):
        """Validate gibberish-specific configuration."""
        if not (0.0 <= self.prob_threshold <= 1.0):
            raise ValueError("prob_threshold must be between 0.0 and 1.0")


@dataclass
class LanguageGuardrailConfig(GuardrailConfig):
    """Configuration for Language Detection Guardrail.

    Attributes:
        allowed_languages: List of ISO language codes (e.g.,
            ``["en", "fr"]``).
        enable_script_prefilter: When True, run a fast Unicode-script
            prefilter (CJK, Cyrillic, Arabic, etc.) that short-circuits
            requests whose dominant script is unambiguously outside
            ``allowed_languages``. The LLM still handles Latin-script
            disambiguation (since Latin covers 100+ languages). Disable
            to force every check through the LLM.
    """

    allowed_languages: Optional[list[str]] = (
        None  # List of ISO language codes (e.g., ["en", "fr"])
    )
    enable_script_prefilter: bool = True

    def __post_init__(self):
        """Validate language-specific configuration."""
        if self.allowed_languages is None:
            raise ValueError("allowed_languages is required")
        if not self.allowed_languages:
            raise ValueError("allowed_languages cannot be empty")


@dataclass
class ToneGuardrailConfig(GuardrailConfig):
    """Configuration for Tone/Sentiment Guardrail."""

    desired_tone: str = "polite"
    unwanted_tones: Optional[list[str]] = None

    def __post_init__(self):
        """Validate tone-specific configuration."""
        if self.unwanted_tones is None:
            self.unwanted_tones = ["aggressive", "rude", "offensive", "sarcastic"]


@dataclass
class GroundingGuardrailConfig(GuardrailConfig):
    """Configuration for Grounding/Hallucination Guardrail."""

    grounding_threshold: float = 0.7  # 0.0 to 1.0

    def __post_init__(self):
        """Validate grounding-specific configuration."""
        if not (0.0 <= self.grounding_threshold <= 1.0):
            raise ValueError("grounding_threshold must be between 0.0 and 1.0")


# Global guardrail configuration
_guardrail_lm = None


def configure(lm=None, **kwargs):
    """Configure DSPy Guardrails with a language model.

    This function works similarly to dspy.configure() but sets up
    configuration specifically for guardrails. If no arguments are provided,
    it will attempt to use the globally configured DSPy LM.

    Args:
        lm: DSPy language model to use for guardrails
        **kwargs: Additional configuration options (reserved for future use)

    Example:
        import dspy
        from dspy_guardrails import configure as guardrails_configure

        # Configure guardrails with a specific model
        lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="key")
        guardrails_configure(lm=lm)

        # Or use the globally configured DSPy LM
        dspy.configure(lm=lm)
        guardrails_configure()  # Uses the global DSPy config
    """
    global _guardrail_lm

    if lm is not None:
        _guardrail_lm = lm
    else:
        # Try to use globally configured DSPy LM
        try:
            import dspy

            if (
                hasattr(dspy, "settings")
                and hasattr(dspy.settings, "lm")
                and dspy.settings.lm is not None
            ):
                _guardrail_lm = dspy.settings.lm
            else:
                raise ValueError(
                    "No language model provided and no global DSPy configuration found. "
                    "Either provide an lm parameter or configure DSPy globally first."
                )
        except ImportError:
            raise ValueError("DSPy not available. Please provide an lm parameter.")


def get_guardrail_lm():
    """Get the configured language model for guardrails.

    Returns:
        The configured DSPy language model

    Raises:
        ValueError: If no language model has been configured
    """
    if _guardrail_lm is None:
        raise ValueError(
            "Guardrails not configured. Call dspy_guardrails.configure() first."
        )
    return _guardrail_lm
