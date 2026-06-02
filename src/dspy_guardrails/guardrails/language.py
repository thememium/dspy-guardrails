"""Language detection and compliance guardrail implementation.

Includes a fast, Unicode-script-based prefilter that runs before the
DSPy LLM call.  The prefilter does **script detection** — if the
input's dominant Unicode script is unambiguously outside
``allowed_languages``, the request is blocked immediately.  Latin
script (which covers 100+ languages) always falls through to the LLM.
"""

import re
from typing import List, Optional, Tuple

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import LanguageGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)

# ---------------------------------------------------------------------------
# Unicode script catalog (import-time, compiled once)
# ---------------------------------------------------------------------------

SCRIPT_TO_LANG_CODES: List[Tuple[str, str, Tuple[str, ...]]] = [
    ("han", r"[\u4E00-\u9FFF\u3400-\u4DBF]", ("zh",)),  # CJK Unified
    ("hiragana_katakana", r"[\u3040-\u309F\u30A0-\u30FF]", ("ja",)),  # Japanese
    (
        "hangul",
        r"[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]",
        ("ko",),
    ),  # Korean
    (
        "cyrillic",
        r"[\u0400-\u04FF\u0500-\u052F]",
        ("ru", "uk", "bg", "sr", "mk"),
    ),  # Russian, Ukrainian, Bulgarian, etc.
    (
        "arabic",
        r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]",
        ("ar", "fa", "ur"),
    ),  # Arabic, Persian, Urdu
    ("hebrew", r"[\u0590-\u05FF]", ("he",)),
    (
        "devanagari",
        r"[\u0900-\u097F]",
        ("hi", "ne", "mr"),
    ),  # Hindi, Nepali, Marathi
    ("thai", r"[\u0E00-\u0E7F]", ("th",)),
    ("greek", r"[\u0370-\u03FF]", ("el",)),
]

# Pre-compiled at import time so every guardrail instance reuses the
# same compiled patterns without re-compiling.
_COMPILED_SCRIPT_CATALOG: List[Tuple[str, re.Pattern[str], Tuple[str, ...]]] = [
    (name, re.compile(pattern), codes) for name, pattern, codes in SCRIPT_TO_LANG_CODES
]

# Minimum number of non-Latin characters required before the prefilter
# will attempt script-based blocking.  Short inputs (< 5 non-Latin
# chars) fall through to the LLM to avoid false positives on
# borrowed words or one-off characters.
_MIN_NON_LATIN_CHARS = 5


# ---------------------------------------------------------------------------
# Module-level helper
# ---------------------------------------------------------------------------


def _detect_dominant_script(text: str) -> Optional[str]:
    """Return the name of the script with the most characters in *text*.

    Returns ``None`` when no non-Latin script characters are found
    (i.e. the text is pure Latin or empty).
    """
    best_name: Optional[str] = None
    best_count = 0

    for name, pattern, _codes in _COMPILED_SCRIPT_CATALOG:
        count = len(pattern.findall(text))
        if count > best_count:
            best_count = count
            best_name = name

    return best_name if best_count > 0 else None


# ---------------------------------------------------------------------------
# DSPy signature
# ---------------------------------------------------------------------------


class GuardrailsLanguageSignature(dspy.Signature):
    """You are a language detection system.
    Identify the language of the input text and determine if it belongs to the allowed language list.

    The detected language should be returned as an ISO 639-1 code (e.g., 'en', 'fr', 'es')."""

    user_input: str = dspy.InputField(desc="The text content to analyze.")
    allowed_languages: List[str] = dspy.InputField(
        desc="List of allowed language codes (e.g., ['en', 'es'])."
    )
    detected_language_code: str = dspy.OutputField(
        desc="The detected ISO 639-1 language code of the input."
    )
    detected_language_name: str = dspy.OutputField(
        desc="The full name of the detected language."
    )
    is_allowed_language: bool = dspy.OutputField(
        desc="True if the detected language is in the allowed list, False otherwise."
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation of the language detection result."
    )


# ---------------------------------------------------------------------------
# Language guardrail
# ---------------------------------------------------------------------------


class LanguageGuardrail(BaseGuardrail):
    """Guardrail for ensuring content is in an allowed language.

    Runs a fast, deterministic Unicode-script prefilter before delegating
    to a DSPy ChainOfThought program for nuanced analysis.  When the
    dominant script is unambiguously outside ``allowed_languages``, the
    LLM call is skipped and ``is_allowed=False``.  Latin-script input
    always falls through to the LLM (Latin covers 100+ languages).
    """

    def __init__(self, config: LanguageGuardrailConfig):
        """Initialize the language guardrail.

        Args:
            config: Configuration for the language guardrail
        """
        super().__init__(config)
        self.config: LanguageGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsLanguageSignature)

        # Precomputed script catalog for this instance.  Uses the
        # globally compiled patterns but stores them on the instance
        # so tests can inspect ``_script_catalog`` directly.
        self._script_catalog: List[Tuple[str, re.Pattern[str], Tuple[str, ...]]] = list(
            _COMPILED_SCRIPT_CATALOG
        )

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "language"

    def _configure_dspy(self) -> None:
        """Configure DSPy for language guardrail."""
        configure_dspy_from_config(self.config)

    # ------------------------------------------------------------------ #
    # Prefilter                                                            #
    # ------------------------------------------------------------------ #

    def _run_script_prefilter(self, input_text: str) -> Optional[str]:
        """Run the script-based prefilter.  Returns the script name to
        block, or ``None`` to fall through to the LLM.

        Skipped when:
        * The prefilter is disabled in config.
        * The input is empty or has fewer than ``_MIN_NON_LATIN_CHARS``
          non-Latin characters (too short to judge reliably).
        * The dominant script's associated ISO codes overlap with
          ``config.allowed_languages`` (the LLM still handles the
          finer-grained distinction).
        """
        if not self.config.enable_script_prefilter:
            return None

        if not input_text or not input_text.strip():
            return None

        # Count total non-Latin characters across all scripts.
        total_non_latin = sum(
            len(pattern.findall(input_text))
            for _name, pattern, _codes in self._script_catalog
        )
        if total_non_latin < _MIN_NON_LATIN_CHARS:
            return None

        script = _detect_dominant_script(input_text)
        if script is None:
            return None

        # Look up the ISO codes associated with the dominant script.
        allowed = set(self.config.allowed_languages or [])
        for name, _pattern, codes in self._script_catalog:
            if name == script:
                if any(code in allowed for code in codes):
                    return None  # allowed — fall through to LLM
                return script  # blocked

        return None  # unknown script — fall through to LLM

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text language is allowed.

        The script prefilter runs first.  On a match the LLM is skipped
        and ``is_allowed=False``.  Otherwise the DSPy LLM handles
        fine-grained language detection.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if language is allowed
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

        # 1. Fast script prefilter.  On match, skip the LLM.
        script = self._run_script_prefilter(input_text)
        if script is not None:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Language not in allowed list (script: {script})",
                metadata={
                    "method": "regex_prefilter",
                    "is_allowed_language": False,
                    "detected_script": script,
                    "allowed_languages": self.config.allowed_languages,
                },
                guardrail_name=self.name,
            )

        # 2. LLM-based analysis via DSPy.
        try:
            result = self._program(
                user_input=input_text,
                allowed_languages=self.config.allowed_languages,
            )

            is_allowed = result.is_allowed_language
            reason = None
            if not is_allowed:
                reason = (
                    result.reason
                    or f"Language '{result.detected_language_name}' ({result.detected_language_code}) is not allowed."
                )

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "detected_language_code": result.detected_language_code,
                    "detected_language_name": result.detected_language_name,
                    "allowed_languages": self.config.allowed_languages,
                    "explanation": result.reason,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during language check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
