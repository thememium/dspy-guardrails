import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", sql_output="polars")

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    import re
    from dataclasses import dataclass
    from typing import List, Dict, Any, Optional
    from enum import Enum


@app.class_definition
@dataclass
class KeywordsConfig:
    """Configuration schema for the keywords guardrail."""
    keywords: List[str]

    def __post_init__(self):
        if not self.keywords:
            raise ValueError("keywords list cannot be empty")


@app.class_definition
@dataclass
class KeywordsContext:
    """Context requirements for the keywords guardrail."""
    pass


@app.class_definition
@dataclass
class GuardrailResult:
    """Result from the keywords guardrail check."""
    tripwire_triggered: bool
    info: Dict[str, Any]


@app.cell
def _():
    # Unicode-aware word character detection (equivalent to TypeScript's WORD_CHAR_CLASS)
    WORD_CHAR_CLASS = r'[\w\p{L}\p{N}]'  # \w already includes letters, digits, underscore

    def is_word_char(char: Optional[str]) -> bool:
        """Check if a character is a word character (Unicode-aware)."""
        if not char:
            return False
        # Use regex to check for word characters including Unicode letters and numbers
        pattern = re.compile(WORD_CHAR_CLASS, re.UNICODE)
        return bool(pattern.match(char))
    return WORD_CHAR_CLASS, is_word_char


@app.cell
def _(WORD_CHAR_CLASS, is_word_char):
    class KeywordsGuardrail:
        """Keywords-based content filtering guardrail."""

        def check(self, ctx: KeywordsContext, text: str, config: KeywordsConfig) -> GuardrailResult:
            """
            Check if any of the configured keywords appear in the input text.

            Args:
                ctx: Runtime context (unused for this guardrail)
                text: Input text to check
                config: Configuration specifying keywords

            Returns:
                GuardrailResult indicating if tripwire was triggered
            """
            keywords = config.keywords

            # Sanitize keywords by stripping trailing punctuation
            sanitized_keywords = [k.rstrip('.,!?:;') for k in keywords]

            # Prepare keyword entries with escaped patterns
            keyword_entries = []
            for sanitized in sanitized_keywords:
                if sanitized:  # Skip empty strings after sanitization
                    escaped = re.escape(sanitized)
                    keyword_entries.append({
                        'sanitized': sanitized,
                        'escaped': escaped
                    })

            if not keyword_entries:
                return GuardrailResult(
                    tripwire_triggered=False,
                    info={
                        'matched_keywords': [],
                        'original_keywords': keywords,
                        'sanitized_keywords': sanitized_keywords,
                        'total_keywords': len(keywords),
                        'text_length': len(text),
                    }
                )

            # Build keyword patterns with unicode-aware word boundaries
            keyword_patterns = []
            for entry in keyword_entries:
                sanitized = entry['sanitized']
                escaped = entry['escaped']

                keyword_chars = list(sanitized)
                first_char = keyword_chars[0] if keyword_chars else ''
                last_char = keyword_chars[-1] if keyword_chars else ''

                needs_left_boundary = is_word_char(first_char)
                needs_right_boundary = is_word_char(last_char)

                left_boundary = f'(?<!{WORD_CHAR_CLASS})' if needs_left_boundary else ''
                right_boundary = f'(?!{WORD_CHAR_CLASS})' if needs_right_boundary else ''

                pattern = f'{left_boundary}{escaped}{right_boundary}'
                keyword_patterns.append(pattern)

            # Combine all patterns
            pattern_text = f'(?:{"|".join(keyword_patterns)})'
            pattern = re.compile(pattern_text, re.IGNORECASE | re.UNICODE)

            # Find all matches and collect unique ones (case-insensitive)
            matches = []
            seen = set()
            for match in pattern.finditer(text):
                matched_text = match.group(0)
                lower_match = matched_text.lower()
                if lower_match not in seen:
                    matches.append(matched_text)
                    seen.add(lower_match)

            tripwire_triggered = len(matches) > 0

            return GuardrailResult(
                tripwire_triggered=tripwire_triggered,
                info={
                    'matched_keywords': matches,
                    'original_keywords': keywords,
                    'sanitized_keywords': sanitized_keywords,
                    'total_keywords': len(keywords),
                    'text_length': len(text),
                }
            )

    # Create guardrail instance
    guardrail = KeywordsGuardrail()
    return


if __name__ == "__main__":
    app.run()
