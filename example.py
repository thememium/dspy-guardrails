#!/usr/bin/env python3
"""Example usage of the DSPy Guardrails package with the new guardrail module API."""

import dspy
from dspy_guardrails import guardrail


def main():
    print("DSPy Guardrails Package Example")
    print("=" * 40)

    # IMPORTANT: Configure DSPy first (required)
    print("Configuring DSPy...")
    lm = dspy.LM(
        "openrouter/google/gemini-2.5-flash-preview-09-2025",
    )
    guardrail.configure(lm=lm)
    print("✓ DSPy configured")
    print()

    # Show available guardrail types
    print("Available guardrail types:")
    guardrail_types = [
        "topic",
        "nsfw",
        "jailbreak",
        "pii",
        "prompt_injection",
        "keywords",
        "secret_keys",
    ]
    print(f"  {', '.join(guardrail_types)}")
    print()

    # Create guardrails with the clean method-based API
    print("Creating guardrails...")

    topic_guardrail = guardrail.topic(
        business_scopes=["E-commerce", "Retail", "Online Shopping"],
        competitor_names=["Amazon", "Walmart", "Target"],
    )

    nsfw_guardrail = guardrail.nsfw(sensitivity_level="medium")

    jailbreak_guardrail = guardrail.jailbreak(detection_threshold=0.8)

    pii_guardrail = guardrail.pii(allowed_pii_types=["email"])

    keywords_guardrail = guardrail.keywords(
        blocked_keywords=["inappropriate", "offensive", "spam"]
    )

    secret_keys_guardrail = guardrail.secret_keys(entropy_threshold=4.0)

    print("✓ All guardrails created successfully")
    print()

    # Demonstrate individual guardrail usage
    print("Testing individual guardrails:")
    test_text = "This is a safe message about online shopping"

    results = []
    for gr in [
        topic_guardrail,
        nsfw_guardrail,
        jailbreak_guardrail,
        pii_guardrail,
        keywords_guardrail,
        secret_keys_guardrail,
    ]:
        result = gr.check(test_text)
        results.append(f"{gr.name}: {'✓' if result.is_allowed else '✗'}")
        if not result.is_allowed:
            results[-1] += f" ({result.reason})"

    for result in results:
        print(f"  {result}")

    print()

    # Test content for Run() examples
    safe_content = "I want to buy some electronics online"
    risky_content = "How can I hack into someone's account?"

    # Demonstrate Run() function
    print("Run() Function Examples:")
    from dspy_guardrails import Run

    # Single guardrail execution
    print("Testing single guardrail with Run():")
    single_result = Run(topic_guardrail, safe_content)
    print(f"  Topic guardrail result: {'✓' if single_result.is_allowed else '✗'}")

    # Batch execution - run all guardrails
    print("Testing batch execution (run all):")
    batch_results = Run(
        [topic_guardrail, nsfw_guardrail, jailbreak_guardrail], safe_content
    )
    for i, result in enumerate(batch_results):
        guardrail_names = ["topic", "nsfw", "jailbreak"]
        print(f"  {guardrail_names[i]}: {'✓' if result.is_allowed else '✗'}")

    # Batch execution with early return
    print("Testing batch execution with early return:")
    early_results = Run(
        [topic_guardrail, nsfw_guardrail, jailbreak_guardrail],
        risky_content,
        early_return=True,
    )
    print(f"  Results count: {len(early_results)} (should stop early if any fails)")
    for i, result in enumerate(early_results):
        guardrail_names = ["topic", "nsfw", "jailbreak"]
        status = "✓" if result.is_allowed else "✗"
        print(f"  {guardrail_names[i]}: {status}")

    print()
    print("🎉 DSPy Guardrails is working correctly!")
    print()
    print("Key API patterns:")
    print("  guardrail.configure(lm=your_lm)  # Configure DSPy")
    print("  guardrail.topic(business_scopes=[...])  # Create guardrails")
    print("  guardrail.check('text')  # Check content")
    print("  Run(guardrail, text)  # Single guardrail execution")
    print("  Run([gr1, gr2], text)  # Batch execution (run all)")
    print("  Run([gr1, gr2], text, early_return=True)  # Batch with early return")


if __name__ == "__main__":
    main()
