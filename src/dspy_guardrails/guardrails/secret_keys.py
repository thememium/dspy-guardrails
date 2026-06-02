"""Secret keys detection guardrail implementation.

Includes a fast, regex-based prefilter that runs before the DSPy LLM call.
The prefilter handles well-known provider key formats — OpenAI, Anthropic,
GitHub PATs, AWS access keys, Google API keys, Slack tokens, Stripe keys,
SendGrid, HuggingFace tokens, JWTs, PEM private keys, and Bearer/Basic
auth headers — with a uniform ``block`` action (secrets are binary: if
detected, the request is rejected). Custom user patterns (with optional
labels) are supported and ReDoS-screened at construction time. User-
supplied key-prefix patterns are entropy-filtered to reduce false
positives on short prefixes like ``"key"`` or ``"token"``.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import SecretKeysGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)

# --------------------------------------------------------------------------- #
# Built-in secret-key regex catalog                                            #
# --------------------------------------------------------------------------- #

SECRET_KEY_PATTERNS: Dict[str, str] = {
    "openai_api_key": r"\bsk-[A-Za-z0-9]{20,}",
    "openai_project_key": r"\bsk-proj-[A-Za-z0-9_\-]{40,}",
    "openai_service_key": r"\bsk-svcacct-[A-Za-z0-9_\-]{40,}",
    "anthropic_api_key": r"\bsk-ant-[A-Za-z0-9_\-]{40,}",
    "github_pat": r"\bghp_[A-Za-z0-9]{36}\b",
    "github_fine_grained": r"\bgithub_pat_[A-Za-z0-9_]{82}\b",
    "github_oauth": r"\bgho_[A-Za-z0-9]{36}\b",
    "github_server": r"\bghs_[A-Za-z0-9]{36}\b",
    "github_user": r"\bghu_[A-Za-z0-9]{36}\b",
    "github_refresh": r"\bghr_[A-Za-z0-9]{36}\b",
    "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
    "aws_session_key": r"\bASIA[0-9A-Z]{16}\b",
    "google_api_key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
    "slack_token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b",
    "slack_webhook": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
    "stripe_live_key": r"\bsk_live_[0-9a-zA-Z]{24,}\b",
    "stripe_test_key": r"\bsk_test_[0-9a-zA-Z]{24,}\b",
    "stripe_restricted": r"\brk_live_[0-9a-zA-Z]{24,}\b",
    "sendgrid_key": r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b",
    "huggingface_token": r"\bhf_[A-Za-z0-9]{34,}\b",
    "jwt_token": r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b",
    "pem_private_key": r"-----BEGIN (RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----",
    "bearer_token": r"(?i)\bbearer\s+[A-Za-z0-9_\-\.=]{20,}",
    "basic_auth_header": r"(?i)\bauthorization:\s*basic\s+[A-Za-z0-9+/=]{8,}",
}


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
# Entropy helper                                                               #
# --------------------------------------------------------------------------- #


def _shannon_entropy(s: str) -> float:
    """Compute Shannon entropy (bits per character) of *s*.

    Returns 0.0 for empty strings.
    """
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


# --------------------------------------------------------------------------- #
# Prefilter result type                                                         #
# --------------------------------------------------------------------------- #


@dataclass
class _SecretMatch:
    """One regex prefilter hit."""

    slug: str
    matched_text: str
    entropy: float


# --------------------------------------------------------------------------- #
# Secret keys guardrail                                                        #
# --------------------------------------------------------------------------- #


class GuardrailsSecretKeysSignature(dspy.Signature):
    """You are a security system that detects secret keys, API tokens, and other sensitive credentials in text.

    Your task is to identify potentially leaked secrets that should not be exposed in logs, code, or user content.

    Common types of secrets to detect:
    - API keys and tokens (AWS, OpenAI, GitHub, etc.)
    - Private keys and certificates
    - Passwords and authentication credentials
    - Database connection strings
    - Encryption keys
    - Access tokens and bearer tokens
    - Webhook secrets
    - Any other sensitive authentication material

    Look for patterns like:
    - Common prefixes (sk-, pk_, AKIA, ghp_, xox, etc.)
    - Long alphanumeric strings that look like keys
    - Base64-encoded data that might be secrets
    - Environment variable names containing secrets
    - Code comments or logs that accidentally include secrets

    Consider entropy - random-looking strings are more likely to be secrets.
    Be cautious about false positives - not every long string is a secret."""

    key_patterns: List[str] = dspy.InputField(
        desc="List of known key patterns or prefixes to look for."
    )
    entropy_threshold: float = dspy.InputField(
        desc="Minimum entropy threshold for detecting potential secrets (0-10)."
    )
    user_input: str = dspy.InputField(
        desc="The text content to analyze for secret keys."
    )
    detected_secrets: Optional[List[str]] = dspy.OutputField(
        desc="List of detected secret strings. Empty if no secrets found."
    )
    secret_types: Optional[List[str]] = dspy.OutputField(
        desc="List of secret types detected (e.g., 'api_key', 'password', 'token'). Empty if no secrets found."
    )
    risk_level: str = dspy.OutputField(
        desc="Risk assessment: 'low', 'medium', 'high', or 'critical'."
    )
    secrets_detected: bool = dspy.OutputField(
        desc="Boolean indicating if any secrets were detected. True if secrets found, False if clean."
    )


class SecretKeysGuardrail(BaseGuardrail):
    """Guardrail for detecting secret keys and sensitive credentials.

    Runs a fast, deterministic regex prefilter (built-in provider catalog
    plus user-supplied custom patterns and key-prefix patterns) before
    delegating to a DSPy ChainOfThought program for nuanced analysis.
    All prefilter matches use the ``block`` action — secrets are binary:
    if detected, the request is rejected with ``is_allowed=False``.
    """

    def __init__(self, config: SecretKeysGuardrailConfig):
        """Initialize the secret keys guardrail.

        Args:
            config: Configuration for the secret keys guardrail
        """
        super().__init__(config)
        self.config: SecretKeysGuardrailConfig = config
        self._program = dspy.ChainOfThought(GuardrailsSecretKeysSignature)

        # Build key_patterns for DSPy fallback (unchanged behaviour).
        self._key_patterns = self.config.key_patterns or [
            "sk-",
            "sk_",
            "pk_",
            "pk-",
            "ghp_",
            "AKIA",
            "xox",
            "SG.",
            "hf_",
            "api-",
            "token",
            "secret",
            "password",
            "key",
            "Bearer ",
            "Authorization:",
            "API_KEY",
            "SECRET_KEY",
        ]

        # --- Compile built-in regex catalog (unless disabled) ---
        self._compiled_patterns: Dict[str, re.Pattern[str]] = {}

        if self.config.enable_regex_prefilter:
            for slug, pat in SECRET_KEY_PATTERNS.items():
                self._compiled_patterns[slug] = re.compile(pat)

        # --- Compile custom patterns (always, independent of prefilter flag) ---
        self._compiled_custom: Dict[str, re.Pattern[str]] = {}
        self._custom_labels: Dict[str, str] = {}

        for entry in self.config.custom_patterns or []:
            name = entry["name"]
            pattern = entry["pattern"]
            # ReDoS validation
            if _is_unsafe_pattern(pattern):
                raise ValueError(
                    f"custom_patterns[{name!r}].pattern is "
                    f"rejected: contains nested quantifiers or "
                    f"overlapping alternations that could cause "
                    f"catastrophic backtracking (ReDoS)"
                )
            self._compiled_custom[name] = re.compile(pattern)
            self._custom_labels[name] = entry.get("label") or name

        # --- Compile user-supplied prefix patterns ---
        self._compiled_user_prefixes: Dict[str, re.Pattern[str]] = {}

        for prefix in self.config.key_patterns or []:
            escaped = re.escape(prefix)
            pat = re.compile(rf"\b{escaped}[A-Za-z0-9_\-]{{20,}}")
            self._compiled_user_prefixes[f"user:{prefix}"] = pat

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "secret_keys"

    def _configure_dspy(self) -> None:
        """Configure DSPy for secret keys guardrail."""
        configure_dspy_from_config(self.config)

    # ------------------------------------------------------------------ #
    # Prefilter                                                            #
    # ------------------------------------------------------------------ #

    def _find_matches(self, text: str) -> List[_SecretMatch]:
        """Run all compiled patterns and return a list of matches.

        Each match records its slug, the matched text, and the Shannon
        entropy of the alphanumeric portion. For built-in and custom
        patterns the entropy is informational only; for user-prefix
        patterns matches below ``config.entropy_threshold`` are
        discarded (the built-in regexes already encode sufficient
        length constraints).
        """
        matches: List[_SecretMatch] = []

        # Built-in catalog.
        for slug, pat in self._compiled_patterns.items():
            for m in pat.finditer(text):
                # Extract the alphanumeric portion for entropy.
                raw = m.group(0)
                alnum = re.sub(r"[^A-Za-z0-9]", "", raw)
                entropy = _shannon_entropy(alnum) if alnum else 0.0
                matches.append(
                    _SecretMatch(
                        slug=slug,
                        matched_text=raw,
                        entropy=entropy,
                    )
                )

        # Custom patterns.
        for name, pat in self._compiled_custom.items():
            for m in pat.finditer(text):
                raw = m.group(0)
                alnum = re.sub(r"[^A-Za-z0-9]", "", raw)
                entropy = _shannon_entropy(alnum) if alnum else 0.0
                matches.append(
                    _SecretMatch(
                        slug=f"custom:{name}",
                        matched_text=raw,
                        entropy=entropy,
                    )
                )

        # User-prefix patterns — filter by entropy threshold.
        threshold = self.config.entropy_threshold
        for prefix_slug, pat in self._compiled_user_prefixes.items():
            for m in pat.finditer(text):
                raw = m.group(0)
                alnum = re.sub(r"[^A-Za-z0-9]", "", raw)
                entropy = _shannon_entropy(alnum) if alnum else 0.0
                if entropy >= threshold:
                    matches.append(
                        _SecretMatch(
                            slug=prefix_slug,
                            matched_text=raw,
                            entropy=entropy,
                        )
                    )

        return matches

    def _run_regex_prefilter(self, input_text: str) -> List[_SecretMatch]:
        """Run the prefilter. Returns the list of matches (empty if none)."""
        return self._find_matches(input_text)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(self, input_text: str, **kwargs) -> GuardrailResult:
        """Check if the input text contains secret keys or sensitive credentials.

        The regex prefilter runs first. On any match the LLM is skipped
        and ``is_allowed=False`` with ``method="regex_prefilter"`` in the
        metadata. Only when no regex match is found do we fall through
        to the DSPy LLM.

        Args:
            input_text: The text content to analyze
            **kwargs: Additional parameters for the check

        Returns:
            GuardrailResult indicating if content contains secrets
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
            matches = self._run_regex_prefilter(input_text)
            if matches:
                slugs = sorted({m.slug for m in matches})
                return GuardrailResult(
                    is_allowed=False,
                    reason=f"Secret detected: {', '.join(slugs)}",
                    metadata={
                        "method": "regex_prefilter",
                        "secrets_detected": True,
                        "detected_secrets": [m.matched_text for m in matches],
                        "matches": [
                            {
                                "slug": m.slug,
                                "matched_text": m.matched_text,
                                "entropy": round(m.entropy, 3),
                            }
                            for m in matches
                        ],
                    },
                    guardrail_name=self.name,
                )

        # 2. LLM-based analysis via DSPy.
        try:
            result = self._program(
                key_patterns=self._key_patterns,
                entropy_threshold=self.config.entropy_threshold,
                user_input=input_text,
            )

            is_allowed = not result.secrets_detected

            reason = None
            if result.secrets_detected and result.detected_secrets:
                detected = ", ".join(result.detected_secrets[:3])
                if len(result.detected_secrets) > 3:
                    detected += f" (+{len(result.detected_secrets) - 3} more)"
                reason = f"Potential secrets detected: {detected}"

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "secrets_detected": result.secrets_detected,
                    "detected_secrets": result.detected_secrets or [],
                    "secret_types": result.secret_types or [],
                    "risk_level": result.risk_level,
                    "key_patterns": self._key_patterns,
                    "entropy_threshold": self.config.entropy_threshold,
                    "method": "dspy",
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during secret detection: {str(e)}",
                metadata={"error": str(e), "method": "dspy"},
                guardrail_name=self.name,
            )
