"""Configuration classes for DSPy Guardrails."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GuardrailConfig:
    """Base configuration class for all guardrails.

    This class provides common configuration options that apply to all guardrails.
    Specific guardrails can extend this class with their own configuration options.
    """

    # DSPy configuration
    model: str = "openrouter/google/gemini-2.5-flash-preview-09-2025"
    temperature: float = 0.0
    max_tokens: Optional[int] = None

    # General settings
    cache_enabled: bool = False
    timeout_seconds: Optional[float] = None

    # Environment variables
    api_key_env_var: str = "OPENROUTER_API_KEY"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not isinstance(self.temperature, (int, float)):
            raise ValueError("temperature must be a number")
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass
class TopicGuardrailConfig(GuardrailConfig):
    """Configuration for Topic Compliance Guardrail."""

    business_scopes: list[str] = None  # type: ignore
    competitor_names: list[str] = None  # type: ignore

    def __post_init__(self):
        """Validate topic-specific configuration."""
        super().__post_init__()
        if self.business_scopes is None:
            raise ValueError("business_scopes is required")
        if self.competitor_names is None:
            raise ValueError("competitor_names is required")
        if not self.business_scopes:
            raise ValueError("business_scopes cannot be empty")
        if not self.competitor_names:
            raise ValueError("competitor_names cannot be empty")


@dataclass
class NsfwGuardrailConfig(GuardrailConfig):
    """Configuration for NSFW Detection Guardrail."""

    sensitivity_level: str = "medium"  # low, medium, high

    def __post_init__(self):
        """Validate NSFW-specific configuration."""
        super().__post_init__()
        if self.sensitivity_level not in ["low", "medium", "high"]:
            raise ValueError("sensitivity_level must be 'low', 'medium', or 'high'")


@dataclass
class JailbreakGuardrailConfig(GuardrailConfig):
    """Configuration for Jailbreak Detection Guardrail."""

    detection_threshold: float = 0.8  # 0.0 to 1.0

    def __post_init__(self):
        """Validate jailbreak-specific configuration."""
        super().__post_init__()
        if not (0.0 <= self.detection_threshold <= 1.0):
            raise ValueError("detection_threshold must be between 0.0 and 1.0")


@dataclass
class PiiGuardrailConfig(GuardrailConfig):
    """Configuration for PII Detection Guardrail."""

    allowed_pii_types: Optional[list[str]] = None  # If None, all PII is blocked

    def __post_init__(self):
        """Validate PII-specific configuration."""
        super().__post_init__()
        if self.allowed_pii_types is None:
            self.allowed_pii_types = []


@dataclass
class PromptInjectionGuardrailConfig(GuardrailConfig):
    """Configuration for Prompt Injection Guardrail."""

    injection_patterns: Optional[list[str]] = None

    def __post_init__(self):
        """Validate prompt injection-specific configuration."""
        super().__post_init__()
        if self.injection_patterns is None:
            self.injection_patterns = []


@dataclass
class KeywordsGuardrailConfig(GuardrailConfig):
    """Configuration for Keyword Filtering Guardrail."""

    blocked_keywords: list[str] = None  # type: ignore
    case_sensitive: bool = False

    def __post_init__(self):
        """Validate keywords-specific configuration."""
        super().__post_init__()
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
        super().__post_init__()
        if self.key_patterns is None:
            self.key_patterns = []
        if self.entropy_threshold < 0:
            raise ValueError("entropy_threshold must be non-negative")
