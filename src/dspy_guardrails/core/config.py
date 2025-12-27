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
    """Configuration for Topic Compliance Guardrail."""

    topic_scopes: Optional[list[str]] = None
    blocked_topics: Optional[list[str]] = None

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

    def __post_init__(self):
        """Validate NSFW-specific configuration."""
        if self.sensitivity_level not in ["low", "medium", "high"]:
            raise ValueError("sensitivity_level must be 'low', 'medium', or 'high'")


@dataclass
class JailbreakGuardrailConfig(GuardrailConfig):
    """Configuration for Jailbreak Detection Guardrail."""

    detection_threshold: float = 0.8  # 0.0 to 1.0

    def __post_init__(self):
        """Validate jailbreak-specific configuration."""
        if not (0.0 <= self.detection_threshold <= 1.0):
            raise ValueError("detection_threshold must be between 0.0 and 1.0")


@dataclass
class PiiGuardrailConfig(GuardrailConfig):
    """Configuration for PII Detection Guardrail."""

    allowed_pii_types: Optional[list[str]] = None  # If None, all PII is blocked

    def __post_init__(self):
        """Validate PII-specific configuration."""
        if self.allowed_pii_types is None:
            self.allowed_pii_types = []


@dataclass
class PromptInjectionGuardrailConfig(GuardrailConfig):
    """Configuration for Prompt Injection Guardrail."""

    injection_patterns: Optional[list[str]] = None

    def __post_init__(self):
        """Validate prompt injection-specific configuration."""
        if self.injection_patterns is None:
            self.injection_patterns = []


@dataclass
class KeywordsGuardrailConfig(GuardrailConfig):
    """Configuration for Keyword Filtering Guardrail."""

    blocked_keywords: Optional[list[str]] = None
    case_sensitive: bool = False

    def __post_init__(self):
        """Validate keywords-specific configuration."""
        if self.blocked_keywords is None:
            raise ValueError("blocked_keywords is required")
        if not self.blocked_keywords:
            raise ValueError("blocked_keywords cannot be empty")


@dataclass
class SecretKeysGuardrailConfig(GuardrailConfig):
    """Configuration for Secret Keys Detection Guardrail."""

    key_patterns: Optional[list[str]] = None
    entropy_threshold: float = 4.0

    def __post_init__(self):
        """Validate secret keys-specific configuration."""
        if self.key_patterns is None:
            self.key_patterns = []
        if self.entropy_threshold < 0:
            raise ValueError("entropy_threshold must be non-negative")


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
