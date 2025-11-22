import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", sql_output="polars")

with app.setup:
    # Initialization code that runs before all other cells
    import re
    from typing import Any, Dict, List

    import marimo as mo


@app.function
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
            keyword_entries.append(
                {"sanitized": sanitized, "escaped": escaped}
            )

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

    # Apply word boundaries per keyword for matching
    keyword_patterns = []
    for entry in keyword_entries:
        sanitized = entry["sanitized"]
        escaped = entry["escaped"]

        # Check if keyword starts/ends with word characters for boundary needs
        needs_left_boundary = sanitized and (
            sanitized[0].isalnum() or sanitized[0] == "_"
        )
        needs_right_boundary = sanitized and (
            sanitized[-1].isalnum() or sanitized[-1] == "_"
        )

        left_boundary = r"\b" if needs_left_boundary else ""
        right_boundary = r"\b" if needs_right_boundary else ""

        pattern = f"{left_boundary}{escaped}{right_boundary}"
        keyword_patterns.append(pattern)

    # Create combined regex pattern
    pattern_text = f"(?:{'|'.join(keyword_patterns)})"
    pattern = re.compile(
        pattern_text, re.IGNORECASE
    )  # Unicode is default in Python 3

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
    return keywords_input, text_input


@app.cell
def _(keywords_input):
    keywords_input
    return


@app.cell
def _(text_input):
    text_input
    return


@app.cell
def c_program_results(keywords_input, text_input):
    result = None

    if keywords_input.value and text_input.value:
        # Process keywords - split by newlines and strip whitespace
        keywords = [
            k.strip() for k in keywords_input.value.split("\n") if k.strip()
        ]
        text = text_input.value

        print(text)

        result = keywords_check(text=text, keywords=keywords)
    return (result,)


@app.cell
def _(result):
    result
    return


@app.cell
def c_results(result):
    md_result = None

    if result:
        # Display main result
        status = (
            "🚨 TRIPWIRE TRIGGERED"
            if result["tripwireTriggered"]
            else "✅ OK - No keywords detected"
        )
        md_result = mo.md(f"### Result\n\n**Status:** {status}")

        # Display matched keywords if any
        if result["info"]["matchedKeywords"]:
            md_result = mo.md("**Matched Keywords:**")
            for keyword in result["info"]["matchedKeywords"]:
                md_result = mo.md(f"- `{keyword}`")

        # Display details
        md_result = mo.md(
            f"**\nDetails:**\n- **Total keywords checked:** {result['info']['totalKeywords']}\n- **Text length:** {result['info']['textLength']} characters"
        )

        # Show original and sanitized keywords
        if (
            result["info"]["originalKeywords"]
            != result["info"]["sanitizedKeywords"]
        ):
            md_result = mo.md("**Keyword processing:**")
            for orig, san in zip(
                result["info"]["originalKeywords"],
                result["info"]["sanitizedKeywords"],
            ):
                if orig != san:
                    md_result = mo.md(
                        f"- `{orig}` → `{san}` (punctuation stripped)"
                    )
    else:
        md_result = mo.md(
            "**Enter keywords and text above to run the keyword check.**"
        )
    return (md_result,)


@app.cell
def _(md_result):
    md_result
    return


if __name__ == "__main__":
    app.run()
