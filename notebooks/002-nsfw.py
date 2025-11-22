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
                    "HTTP-Referer": "http://dspy-guardrails.local",
                    "X-Title": "dspy guardrails",
                },
                cache=False,
            )
            dspy.configure(lm=lm)
        except RuntimeError:
            pass  # already configured


    config_dspy()
    return


@app.class_definition
class GuardrailsNsfwSignature(dspy.Signature):
    """You are a content moderation assistant.
    Your task is to analyze text and determine if it contains NSFW (Not Safe For Work) content.

    Flag any content that matches these criteria."""

    nsfw_content_types: List[str] = dspy.InputField(
        desc="The defined business scope or topics. A list of topics that are considered on topic."
    )
    user_input: str = dspy.InputField(desc="The text content to analyze.")
    nsfw_reasons: Optional[List[str]] = dspy.OutputField(
        desc="List of reasons why the content is considered NSFW, if applicable. Empty if safe. A single word reason is sufficient."
    )
    is_input_nsfw: bool = dspy.OutputField(
        desc="Boolean indicating if the content is NSFW. True if NSFW, False if safe."
    )


@app.cell
def c_input():
    user_input = mo.ui.text_area().form()
    user_input
    return (user_input,)


@app.cell
def c_program(user_input):
    results = None

    if user_input.value:
        nsfw_content_types = [
            "Sexual content and explicit material",
            "Hate speech and discriminatory language",
            "Harassment and bullying",
            "Violence and gore",
            "Self-harm and suicide references",
            "Profanity and vulgar language",
            "Illegal activities (drugs, theft, weapons, etc.)",
            "Adult themes and mature content",
            "Inappropriate workplace content",
            "Extremist or radical content",
            "Exploitation or abuse",
            "Graphic medical content",
            "Other potentially offensive or inappropriate content",
        ]

        program = dspy.Predict(GuardrailsNsfwSignature)

        results = program(
            nsfw_content_types=nsfw_content_types,
            user_input=user_input.value,
        )
    return (results,)


@app.cell
def c_results(results):
    results
    return


if __name__ == "__main__":
    app.run()
