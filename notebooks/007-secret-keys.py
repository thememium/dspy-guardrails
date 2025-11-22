import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", sql_output="polars")

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    import re
    import math
    from typing import List, Dict, Any, Optional, Tuple
    from dataclasses import dataclass
    from enum import Enum


@app.cell
def _():
    # Configuration and Constants
    class Threshold(Enum):
        STRICT = "strict"
        BALANCED = "balanced"
        PERMISSIVE = "permissive"

    @dataclass
    class SecretKeysConfig:
        threshold: Threshold = Threshold.BALANCED
        custom_regex: Optional[List[str]] = None

    @dataclass
    class GuardrailResult:
        tripwireTriggered: bool
        info: Dict[str, Any]

    # Common key prefixes used in secret keys
    COMMON_KEY_PREFIXES = [
        "key-",
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
        "apikey-",
        "token-",
        "secret-",
        "SHA:",
        "Bearer ",
    ]

    # File extensions to ignore when strict_mode is False
    ALLOWED_EXTENSIONS = [
        ".py",
        ".js",
        ".html",
        ".css",
        ".json",
        ".md",
        ".txt",
        ".csv",
        ".xml",
        ".yaml",
        ".yml",
        ".ini",
        ".conf",
        ".config",
        ".log",
        ".sql",
        ".sh",
        ".bat",
        ".dll",
        ".so",
        ".dylib",
        ".jar",
        ".war",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".ts",
        ".jsx",
        ".vue",
        ".cpp",
        ".c",
        ".h",
        ".cs",
        ".fs",
        ".vb",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
    ]

    # Configuration presets for different sensitivity levels
    CONFIGS = {
        "strict": {
            "min_length": 10,
            "min_entropy": 3.0,
            "min_diversity": 2,
            "strict_mode": True,
        },
        "balanced": {
            "min_length": 10,
            "min_entropy": 3.8,
            "min_diversity": 3,
            "strict_mode": False,
        },
        "permissive": {
            "min_length": 20,
            "min_entropy": 3.5,
            "min_diversity": 2,
            "strict_mode": False,
        },
    }
    return (
        ALLOWED_EXTENSIONS,
        COMMON_KEY_PREFIXES,
        CONFIGS,
        GuardrailResult,
        SecretKeysConfig,
        Threshold,
    )


@app.cell
def _(ALLOWED_EXTENSIONS, COMMON_KEY_PREFIXES):
    # Helper Functions
    def entropy(s: str) -> float:
        """Calculate the Shannon entropy of a string."""
        if len(s) == 0:
            return 0

        counts = {}
        for c in s:
            counts[c] = counts.get(c, 0) + 1

        entropy_val = 0
        for count in counts.values():
            probability = count / len(s)
            entropy_val -= probability * math.log2(probability)

        return entropy_val

    def char_diversity(s: str) -> int:
        """Count the number of character types present in a string."""
        has_lower = any(c.islower() for c in s)
        has_upper = any(c.isupper() for c in s)
        has_digit = any(c.isdigit() for c in s)
        has_special = any(not c.isalnum() for c in s)

        return sum([has_lower, has_upper, has_digit, has_special])

    def contains_allowed_pattern(text: str) -> bool:
        """Check if text contains allowed URL or file extension patterns."""
        # Check if it's a URL pattern
        url_pattern = r"^https?:\/\/[a-zA-Z0-9.-]+\/?[a-zA-Z0-9.\/_-]*$"
        if re.match(url_pattern, text, re.IGNORECASE):
            # If it's a URL, check if it contains any secret patterns
            if any(prefix in text for prefix in COMMON_KEY_PREFIXES):
                return False
            return True

        # Regex for allowed file extensions - must end with the extension
        ext_pattern = (
            r"^[^\s]*("
            + "|".join(ext.replace(".", r"\.") for ext in ALLOWED_EXTENSIONS)
            + r")$"
        )
        return bool(re.match(ext_pattern, text, re.IGNORECASE))
    return char_diversity, contains_allowed_pattern, entropy


@app.cell
def _(
    COMMON_KEY_PREFIXES,
    GuardrailResult,
    char_diversity,
    contains_allowed_pattern,
    entropy,
):
    # Secret Detection Functions
    def is_secret_candidate(
        s: str, cfg: Dict[str, Any], custom_regex: Optional[List[str]] = None
    ) -> bool:
        """Check if a string is a secret key using the specified criteria."""
        # Check custom patterns first if provided
        if custom_regex:
            for pattern in custom_regex:
                try:
                    if re.search(pattern, s):
                        return True
                except re.error:
                    # Invalid regex pattern, skip
                    continue

        if not cfg["strict_mode"] and contains_allowed_pattern(s):
            return False

        long_enough = len(s) >= cfg["min_length"]
        diverse = char_diversity(s) >= cfg["min_diversity"]

        # Check common prefixes first - these should always be detected
        if any(s.startswith(prefix) for prefix in COMMON_KEY_PREFIXES):
            return True

        # For other candidates, check length and diversity
        if not (long_enough and diverse):
            return False

        return entropy(s) >= cfg["min_entropy"]

    def detect_secret_keys(
        text: str, cfg: Dict[str, Any], custom_regex: Optional[List[str]] = None
    ):
        """Detect potential secret keys in text."""
        words = [re.sub(r"[*#]", "", w) for w in text.split()]
        secrets = [w for w in words if is_secret_candidate(w, cfg, custom_regex)]

        # Mask detected secrets in the text
        checked_text = text
        for secret in secrets:
            checked_text = re.sub(re.escape(secret), "<SECRET>", checked_text)

        return GuardrailResult(
            tripwireTriggered=len(secrets) > 0,
            info={
                "guardrail_name": "Secret Keys",
                "detected_secrets": secrets,
                "masked_text": checked_text,
            },
        )
    return (detect_secret_keys,)


@app.cell
def _(CONFIGS, SecretKeysConfig, detect_secret_keys):
    # Main Guardrail Function
    async def secret_keys_check(data, config=None):
        """
        Guardrail function for secret key and credential detection.

        Scans the input for likely secrets or credentials (e.g., API keys, tokens)
        using entropy, diversity, and pattern rules.
        """
        if config is None:
            config = SecretKeysConfig()

        cfg = CONFIGS[config.threshold.value]
        return detect_secret_keys(data, cfg, config.custom_regex)
    return (secret_keys_check,)


@app.cell
def _(SecretKeysConfig, Threshold, secret_keys_check):
    # Example Usage and Testing
    async def test_secret_detection():
        """Test the secret detection with various examples."""
        test_cases = [
            "Here is my API key: sk-1234567890abcdef",
            "Bearer token: xoxb-1234567890123-4567890123456-78901234567890-abcdef123456",
            "GitHub token: ghp_1234567890abcdef1234567890abcdef123456",
            "AWS key: AKIA1234567890123456",
            "Regular text without secrets",
            "File path: /path/to/config.py",
            "URL: https://example.com/api/endpoint",
            "High entropy string: aB3!dE6@gH1#jK2$lM5%nO8&pQ0*",
        ]

        for i, text in enumerate(test_cases, 1):
            print(f"\nTest {i}: {text}")

            # Test with different thresholds
            for threshold in [
                Threshold.STRICT,
                Threshold.BALANCED,
                Threshold.PERMISSIVE,
            ]:
                config = SecretKeysConfig(threshold=threshold)
                result = await secret_keys_check(text, config)

                print(
                    f"  {threshold.value}: {'SECRET DETECTED' if result.tripwireTriggered else 'No secrets'}"
                )
                if result.tripwireTriggered:
                    print(f"    Found: {result.info['detected_secrets']}")

    # Run the test
    import asyncio

    asyncio.run(test_secret_detection())
    return


if __name__ == "__main__":
    app.run()
