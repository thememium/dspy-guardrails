import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", sql_output="polars")

with app.setup:
    # Initialization code that runs before all other cells
    import re
    from typing import Any, Dict, List

    import dspy
    import marimo as mo


def keywords_check(text: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Keywords-based content filtering guardrail.

    This guardrail checks if specified keywords appear in the input text
    and can be configured to trigger tripwires based on keyword matches.

    Args:
        text: Input text to check
        keywords: List of keywords to check for

    Returns:
        Dict containing tripwire trigger status and match information
    """
    WORD_CHAR_CLASS = r"\w"

    def is_word_char(char: str) -> bool:
        """Check if character is a word character (letter, digit, underscore)."""
        if not char:
            return False
        return bool(re.match(WORD_CHAR_CLASS, char))

    # Sanitize keywords by stripping trailing punctuation
    sanitized_keywords = [k.rstrip(".,!?;:") for k in keywords]

    # Prepare keyword entries with escaped versions
    keyword_entries = []
    for sanitized in sanitized_keywords:
        if sanitized:  # Only include non-empty keywords
            escaped = re.escape(sanitized)
            keyword_entries.append({"sanitized": sanitized, "escaped": escaped})

    if not keyword_entries:
        return {
            "tripwireTriggered": False,
            "info": {
                "matchedKeywords": [],
                "originalKeywords": keywords,
                "sanitizedKeywords": sanitized_keywords,
                "totalKeywords": len(keywords),
                "textLength": len(text),
            },
        }

    # Apply word boundaries per keyword for unicode-aware matching
    keyword_patterns = []
    for entry in keyword_entries:
        sanitized = entry["sanitized"]
        escaped = entry["escaped"]

        chars = list(sanitized)
        first_char = chars[0] if chars else ""
        last_char = chars[-1] if chars else ""

        needs_left_boundary = is_word_char(first_char)
        needs_right_boundary = is_word_char(last_char)

        left_boundary = f"(?<!(?u){WORD_CHAR_CLASS})" if needs_left_boundary else ""
        right_boundary = f"(?!{WORD_CHAR_CLASS})" if needs_right_boundary else ""

        pattern = f"{left_boundary}{escaped}{right_boundary}"
        keyword_patterns.append(pattern)

    # Create combined regex pattern
    pattern_text = f"(?:{'|'.join(keyword_patterns)})"
    pattern = re.compile(pattern_text, re.IGNORECASE | re.UNICODE)

    # Find all matches and collect unique ones
    matches = []
    seen = set()

    for match in pattern.finditer(text):
        matched_text = match.group(0)
        key = matched_text.lower()
        if key not in seen:
            matches.append(matched_text)
            seen.add(key)

    tripwire_triggered = len(matches) > 0

    return {
        "tripwireTriggered": tripwire_triggered,
        "info": {
            "matchedKeywords": matches,
            "originalKeywords": keywords,
            "sanitizedKeywords": sanitized_keywords,
            "totalKeywords": len(keywords),
            "textLength": len(text),
        },
    }


@app.cell
def c_config():
    def config_dspy():
        try:
            lm = dspy.LM(
                "openrouter/google/gemini-2.5-flash-preview-09-2025",
                extra_headers={
                    "HTTP-Referer": "http://dspy-keywords.local",
                    "X-Title": "dspy keywords",
                },
                cache=False,
            )
            dspy.configure(lm=lm)
        except RuntimeError:
            pass  # already configured

    config_dspy()
    return


@app.cell
def c_input():
    keywords_input = mo.ui.text_area(
        label="Keywords (one per line)",
        placeholder="Enter keywords to check for, one per line:\nbad\nforbidden\ninappropriate",
        value="bad\nforbidden\ninappropriate",
        rows=5,
    ).form()

    text_input = mo.ui.text_area(
        label="Text to check",
        placeholder="Enter text to analyze for keyword matches...",
        rows=8,
    ).form()

    return (
        keywords_input,
        text_input,
    )


@app.cell
def c_program_results(keywords_input, text_input):
    result = None

    if keywords_input.value and text_input.value:
        # Process keywords - split by newlines and strip whitespace
        keywords = [k.strip() for k in keywords_input.value.split("\n") if k.strip()]
        text = text_input.value

        result = keywords_check(text=text, keywords=keywords)

    return (result,)


@app.cell
def c_results(result):
    if result:
        # Display main result
        status = (
            "🚨 TRIPWIRE TRIGGERED"
            if result["tripwireTriggered"]
            else "✅ OK - No keywords detected"
        )
        mo.md(f"### Result\n\n**Status:** {status}")

        # Display matched keywords if any
        if result["info"]["matchedKeywords"]:
            mo.md("**Matched Keywords:**")
            for keyword in result["info"]["matchedKeywords"]:
                mo.md(f"- `{keyword}`")

        # Display details
        mo.md(
            """
**Details:**
- **Total keywords checked:** {result['info']['totalKeywords']}
- **Text length:** {result['info']['textLength']} characters
        """.format(result=result)
        )

        # Show original and sanitized keywords
        if result["info"]["originalKeywords"] != result["info"]["sanitizedKeywords"]:
            mo.md("**Keyword processing:**")
            for orig, san in zip(
                result["info"]["originalKeywords"], result["info"]["sanitizedKeywords"]
            ):
                if orig != san:
                    mo.md(f"- `{orig}` → `{san}` (punctuation stripped)")
    else:
        mo.md("**Enter keywords and text above to run the keyword check.**")

    return


if __name__ == "__main__":
    app.run()
