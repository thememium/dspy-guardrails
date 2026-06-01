"""PII detection guardrail implementation.

Includes a fast, regex-based prefilter that runs before the DSPy LLM call.
The prefilter handles the common regex-detectable PII types — email
addresses, phone numbers, US Social Security numbers, credit card numbers,
and IPv4 addresses — with per-preset ``redact`` or ``block`` actions
mirroring the OpenRouter Sensitive Info Guardrail spec. Custom user
patterns (with optional labels) are supported and ReDoS-screened at
construction time. NLP-only presets (``person-name``, ``address``) are
out of scope and remain the LLM's responsibility.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import PiiGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)

# Redaction placeholder used when a custom pattern is configured with
# action="redact" but no explicit ``label`` is provided. Built-in
# presets each have their own canonical label (e.g., ``[EMAIL]``).
REDACTED_PLACEHOLDER = "[REDACTED]"

# Built-in regex-detectable PII presets. Maps slug -> (regex, redaction
# label, default action). NLP-only types (``person-name``, ``address``)
# are intentionally omitted - they require Presidio / spaCy and are the
# LLM's responsibility.
PII_PATTERNS: Dict[str, Tuple[str, str, str]] = {
    # RFC-5322 simplified: letters/digits + ``._%+-``, ``@``, domain with
    # at least one dot and a 2+ letter TLD. Word boundaries to avoid
    # matching inside longer identifiers.
    "email": (
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        "redact",
    ),
    # US phone numbers: optional +1, 3-3-4 grouping with separators
    # (space, dash, dot, parens). Word boundaries reduce false positives
    # on dates like ``100-200 BC``.
    "phone": (
        r"(?:(?:\+?1[\s.\-]?)?\(?[0-9]{3}\)?[\s.\-]?[0-9]{3}[\s.\-]?[0-9]{4})\b",
        "[PHONE]",
        "redact",
    ),
    # US SSN: AAA-GG-SSSS. Excludes obviously invalid area numbers
    # (000, 666, 900-999) and all-zero group/serial numbers.
    "ssn": (
        r"\b(?!000|666|9\d{2})[0-8]\d{2}[-\s](?!00)\d{2}[-\s](?!0000)\d{4}\b",
        "[SSN]",
        "redact",
    ),
    # Credit card: 13-19 digit numbers, with optional space or dash
    # separators every 4 digits. Luhn validation is left to the LLM
    # fallback to avoid rejecting valid-looking test cards.
    "credit-card": (
        r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{1,7}\b",
        "[CREDIT_CARD]",
        "redact",
    ),
    # IPv4: full dotted-quad, 0-255 per octet. Excludes partial matches
    # like version numbers (``1.2.3``).
    "ip-address": (
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b",
        "[IP_ADDRESS]",
        "redact",
    ),
}

# Redaction is applied in this order (most specific first) so that
# longer matches (e.g. credit cards) win over shorter overlapping
# matches (e.g. phones) when both could match the same span.
_REDACTION_ORDER: Tuple[str, ...] = (
    "credit-card",
    "ssn",
    "email",
    "phone",
    "ip-address",
)

VALID_ACTIONS: Tuple[str, ...] = ("redact", "block")


# --------------------------------------------------------------------------- #
# ReDoS safety                                                                 #
# --------------------------------------------------------------------------- #


def _is_unsafe_pattern(pattern: str) -> bool:
    """Heuristic ReDoS screen. Returns True for patterns that exhibit the
    canonical catastrophic-backtracking shapes: nested quantifiers
    ``(X+)+``, ``(X*)*``, ``(X+)*``, ``(X*)+`` and overlapping-alternation
    quantifiers ``(X|Y)*``, ``(X|Y)+``.

    This is intentionally a static, conservative check - it rejects a
    small number of safe patterns in exchange for never accepting a
    known-bad one at config time. Matches the documented rule:
    "patterns with nested quantifiers like ``(a+)+`` or ``(a|a)*`` are
    rejected".
    """
    # (X+)+, (X*)+, (X+)*, (X*)*  (no other group nesting for the
    # static check to stay simple)
    if re.search(r"\([^()]*[+*][^()]*\)[+*]", pattern):
        return True
    # (X|Y)+, (X|Y)*  - any alternation inside a quantified group
    if re.search(r"\([^()]*\|[^()]*\)[+*]", pattern):
        return True
    return False


# --------------------------------------------------------------------------- #
# Prefilter result types                                                       #
# --------------------------------------------------------------------------- #


@dataclass
class _PiiMatch:
    """One regex prefilter hit."""

    slug: str
    action: str  # "redact" or "block"
    matched_text: str
    label: str  # redaction label (used for both redacts and block messages)


# --------------------------------------------------------------------------- #
# PII guardrail                                                                #
# --------------------------------------------------------------------------- #


class GuardrailsPiiSignature(dspy.Signature):
    """You are a PII (Personally Identifiable Information) detection system.

    Your task is to analyze text and identify any personally identifiable information.
    PII includes information that can be used to identify, contact, or locate an individual.

    Common types of PII include:
    - Names (full names, first names, last names)
    - Email addresses
    - Phone numbers
    - Physical addresses
    - Social Security Numbers (SSN) or equivalent
    - Driver's license numbers
    - Passport numbers
    - Bank account numbers
    - Credit card numbers
    - IP addresses
    - Medical record numbers
    - Biometric data references
    - Any other information that could identify an individual

    Flag any content that contains PII, even if it's fictional or example data.
    If 'allowed_pii_types' is provided, do not flag those specific types as pii_detected,
    but still list them in pii_types and pii_examples."""

    user_input: str = dspy.InputField(desc="The text content to analyze for PII.")
    allowed_pii_types: List[str] = dspy.InputField(
        desc="List of PII types that are allowed and should not be flagged."
    )
    pii_types: Optional[List[str]] = dspy.OutputField(
        desc="List of all PII types detected (e.g., 'email', 'phone', 'ssn')."
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation of why this content contains or doesn't contain non-allowed PII."
    )
    pii_examples: Optional[List[str]] = dspy.OutputField(
        desc="Specific examples of PII found in the text."
    )
    pii_detected: bool = dspy.OutputField(
        desc="True if any PII NOT in allowed_pii_types was detected, False otherwise."
    )


class PiiGuardrail(BaseGuardrail):
    """Guardrail for detecting Personally Identifiable Information (PII).

    Runs a fast, deterministic regex prefilter (built-in preset catalog
    plus user-supplied custom patterns) before delegating to a DSPy
    ChainOfThought program for nuanced analysis. Each matched preset can
    be configured with either a ``redact`` action (the matched span is
    replaced with a labeled placeholder, ``is_allowed`` stays True, and
    the LLM call is skipped) or a ``block`` action (the request is
    short-circuited with ``is_allowed=False``).
    """

    def __init__(self, config: PiiGuardrailConfig):
        """Initialize the PII guardrail.

        Args:
            config: Configuration for the PII guardrail
        """
        super().__init__(config)
        self.config: PiiGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsPiiSignature)

        # Compile built-in presets unless the user disabled the prefilter.
        # Custom patterns are always compiled (they are independent of
        # the built-in catalog).
        self._compiled_builtins: Dict[str, re.Pattern[str]] = {}
        self._builtin_actions: Dict[str, str] = {}

        if self.config.enable_regex_prefilter:
            allowed = set(self.config.allowed_pii_types or [])
            for slug, (pat, _label, default_action) in PII_PATTERNS.items():
                if slug in allowed:
                    # Legacy: ``allowed_pii_types`` removes the type from
                    # the check entirely.
                    continue
                self._compiled_builtins[slug] = re.compile(pat)
                # User-supplied action overrides the preset's default.
                self._builtin_actions[slug] = (self.config.pii_actions or {}).get(
                    slug, default_action
                )

        self._compiled_custom: Dict[str, re.Pattern[str]] = {
            entry["name"]: re.compile(entry["pattern"])
            for entry in (self.config.custom_patterns or [])
        }
        self._custom_actions: Dict[str, Tuple[str, str]] = {
            entry["name"]: (entry["action"], entry.get("label") or REDACTED_PLACEHOLDER)
            for entry in (self.config.custom_patterns or [])
        }

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "pii"

    def _configure_dspy(self) -> None:
        """Configure DSPy for PII guardrail."""
        configure_dspy_from_config(self.config)

    # ------------------------------------------------------------------ #
    # Prefilter                                                            #
    # ------------------------------------------------------------------ #

    def _find_matches(self, text: str) -> List[_PiiMatch]:
        """Run all built-in + custom patterns and return a list of matches.

        Each match records its slug, action, matched text, and the
        redaction label (or block message label).
        """
        matches: List[_PiiMatch] = []

        for slug, pat in self._compiled_builtins.items():
            action = self._builtin_actions[slug]
            _, label, _ = PII_PATTERNS[slug]
            for m in pat.finditer(text):
                matches.append(
                    _PiiMatch(
                        slug=slug,
                        action=action,
                        matched_text=m.group(0),
                        label=label,
                    )
                )

        for name, pat in self._compiled_custom.items():
            action, label = self._custom_actions[name]
            for m in pat.finditer(text):
                matches.append(
                    _PiiMatch(
                        slug=f"custom:{name}",
                        action=action,
                        matched_text=m.group(0),
                        label=label,
                    )
                )

        return matches

    def _apply_redactions(self, text: str, matches: List[_PiiMatch]) -> str:
        """Apply ``redact`` matches in-place, returning the modified text.

        Block matches are left untouched (the request is being rejected
        anyway). Matches are applied most-specific-first so longer
        patterns (e.g. credit-card) win over shorter ones (e.g. phone)
        when both could match the same span.
        """
        redact_matches = [m for m in matches if m.action == "redact"]
        if not redact_matches:
            return text

        # Process by slug in the canonical order, longest-pattern-first,
        # so e.g. credit-card wins over phone on the same span.
        result = text
        for slug in _REDACTION_ORDER:
            for m in redact_matches:
                if m.slug != slug:
                    continue
                result = result.replace(m.matched_text, m.label, 1)
        # Custom patterns (slug prefix "custom:") are processed last, in
        # the order they were declared.
        for m in redact_matches:
            if not m.slug.startswith("custom:"):
                continue
            result = result.replace(m.matched_text, m.label, 1)
        return result

    def _run_regex_prefilter(
        self, input_text: str
    ) -> Tuple[List[_PiiMatch], Optional[str]]:
        """Run the prefilter. Returns ``(matches, redacted_text)``.

        ``redacted_text`` is ``None`` if no redactions were applied
        (either no matches at all, or all matches are ``block``).
        Block matches short-circuit LLM execution; redact matches do
        too once the redacted text has been produced.
        """
        matches = self._find_matches(input_text)
        if not matches:
            return [], None

        # Block wins over redact (stricter action wins).
        if any(m.action == "block" for m in matches):
            return matches, None

        redacted = self._apply_redactions(input_text, matches)
        return matches, redacted

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains personally identifiable information.

        The regex prefilter runs first. On a ``block`` match the LLM is
        skipped and ``is_allowed=False``. On a ``redact`` match the LLM
        is also skipped but ``is_allowed`` stays True and the modified
        text is exposed via ``metadata["redacted_text"]``. Only when no
        regex match is found do we fall through to the DSPy LLM.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content contains PII
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

        # 1. Fast regex prefilter. On any match, skip the LLM.
        if self.config.enable_regex_prefilter or self._compiled_custom:
            matches, redacted = self._run_regex_prefilter(input_text)
            if matches:
                block_matches = [m for m in matches if m.action == "block"]
                if block_matches:
                    labels = ", ".join(sorted({m.label for m in block_matches}))
                    return GuardrailResult(
                        is_allowed=False,
                        reason=f"PII detected (blocked): {labels}",
                        metadata={
                            "pii_detected": True,
                            "method": "regex_prefilter",
                            "action": "block",
                            "matches": [
                                {
                                    "slug": m.slug,
                                    "matched_text": m.matched_text,
                                    "label": m.label,
                                }
                                for m in matches
                            ],
                        },
                        guardrail_name=self.name,
                    )

                # All matches were redacts -> forward the modified text.
                detected_types = sorted({m.slug for m in matches})
                return GuardrailResult(
                    is_allowed=True,
                    reason=f"PII redacted: {', '.join(detected_types)}",
                    metadata={
                        "pii_detected": True,
                        "method": "regex_prefilter",
                        "action": "redact",
                        "redacted_text": redacted,
                        "pii_types": detected_types,
                        "matches": [
                            {
                                "slug": m.slug,
                                "matched_text": m.matched_text,
                                "label": m.label,
                            }
                            for m in matches
                        ],
                    },
                    guardrail_name=self.name,
                )

        # 2. LLM-based analysis via DSPy.
        try:
            result = self._program(
                user_input=input_text,
                allowed_pii_types=self.config.allowed_pii_types,
            )

            is_allowed = not result.pii_detected

            reason = None
            if result.pii_detected:
                detected_types = result.pii_types or []
                forbidden_types = [
                    t
                    for t in detected_types
                    if t not in (self.config.allowed_pii_types or [])
                ]
                if forbidden_types:
                    reason = f"PII detected: {', '.join(forbidden_types)}"
                else:
                    reason = result.reason or "PII detected"

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "pii_detected": result.pii_detected,
                    "pii_types": result.pii_types or [],
                    "pii_examples": result.pii_examples or [],
                    "explanation": result.reason,
                    "allowed_pii_types": self.config.allowed_pii_types,
                    "method": "dspy",
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during PII check: {str(e)}",
                metadata={"error": str(e), "method": "dspy"},
                guardrail_name=self.name,
            )
