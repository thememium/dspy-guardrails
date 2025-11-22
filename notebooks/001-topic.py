import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", sql_output="polars")

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    import dspy
    from typing import List, Optional


@app.cell
def c_config():
    def config_dspy():
        try:
            lm = dspy.LM(
                "openrouter/google/gemini-2.5-flash-preview-09-2025",
                extra_headers={
                    "HTTP-Referer": "http://dspy-topic.local",
                    "X-Title": "dspy topic",
                },
                cache=False,
            )
            dspy.configure(lm=lm)
        except RuntimeError:
            pass  # already configured


    config_dspy()
    return


@app.class_definition
class TopicSignature(dspy.Signature):
    """You are a content analysis system that determines if text stays on topic.

    Determine if the text stays within the defined business scope. Flag any content that strays from the allowed topics."""

    business_scopes: List[str] = dspy.InputField(
        desc="The defined business scope or topics. A list of topics that are considered on topic."
    )
    competitor_names: List[str] = dspy.InputField(
        desc="List of competitor names to flag if mentioned in the content."
    )
    user_input: str = dspy.InputField(desc="The text content to analyze.")
    off_topic_reasons: Optional[List[str]] = dspy.OutputField(
        desc="List of reasons why the content is off topic, if applicable. Empty if on topic. A single word reason is sufficient."
    )
    is_on_topic: bool = dspy.OutputField(
        desc="Boolean indicating if the content stays on topic. True if on topic, False if off topic."
    )


@app.cell
def c_input():
    user_input = mo.ui.text_area().form()
    user_input
    return (user_input,)


@app.cell
def c_program():
    business_scopes = ["ShipStation", "Shipping Software", "Printing Labels"]
    competitor_names = ["Shipo", "Pirate Ship"]

    program = dspy.ChainOfThought(TopicSignature)
    return business_scopes, competitor_names, program


@app.cell
def c_program_results(business_scopes, competitor_names, program, user_input):
    results = None

    if user_input.value:
        results = program(
            business_scopes=business_scopes,
            competitor_names=competitor_names,
            user_input=user_input.value,
        )
    return (results,)


@app.cell
def c_results(results):
    results
    return


if __name__ == "__main__":
    app.run()
