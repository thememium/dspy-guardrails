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
        "openrouter/google/gemini-3-flash-preview",
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

    # Create guardrails with the clean class-based API
    print("Creating guardrails...")

    topic_guardrail = guardrail.Topic(
        topic_scopes=["E-commerce", "Retail", "Online Shopping"],
        blocked_topics=["Amazon", "Walmart", "Target"],
    )

    nsfw_guardrail = guardrail.Nsfw(sensitivity_level="medium")

    jailbreak_guardrail = guardrail.Jailbreak(detection_threshold=0.8)

    pii_guardrail = guardrail.Pii(allowed_pii_types=["email"])

    keywords_guardrail = guardrail.Keywords(
        blocked_keywords=["inappropriate", "offensive", "spam"]
    )

    secret_keys_guardrail = guardrail.SecretKeys(entropy_threshold=4.0)

    print("✓ All guardrails created successfully")
    print()

    # Demonstrate unified bulk guardrail testing
    print("Testing all guardrails with bulk Run():")
    test_text = "This is a safe message about online shopping"

    all_guardrails = [
        topic_guardrail,
        nsfw_guardrail,
        jailbreak_guardrail,
        pii_guardrail,
        keywords_guardrail,
        secret_keys_guardrail,
    ]

    results = guardrail.Run(all_guardrails, test_text)
    print(f"Overall result: {'✓' if results.is_allowed else '✗'}")
    if not results.is_allowed and results.reason:
        print(f"Reason: {results.reason}")
    print(f"DEBUGPRINT[80]: example.py:72: results={results}")

    # Show individual guardrail results from metadata
    guardrail_names = ["topic", "nsfw", "jailbreak", "pii", "keywords", "secret_keys"]
    if results.metadata and "text_results" in results.metadata:
        text_result = results.metadata["text_results"][0]  # First (only) text
        for i, result in enumerate(text_result["results"]):
            status = "✓" if result.is_allowed else "✗"
            output = f"  {guardrail_names[i]}: {status}"
            if not result.is_allowed and result.reason:
                output += f" ({result.reason})"
            print(output)

    print()

    # Test content for Run() examples
    safe_content = "I want to buy some electronics online"
    risky_content = "How can I hack into someone's account?"

    # Demonstrate Run() function
    print("Run() Function Examples:")

    # Single guardrail execution
    print("Testing single guardrail with Run():")
    single_result = guardrail.Run(topic_guardrail, safe_content)
    # No need for [0] indexing - Run returns single result for single guardrail
    print(f"  Topic guardrail result: {'✓' if single_result.is_allowed else '✗'}")

    # Batch execution - run all guardrails
    print("Testing batch execution (run all):")
    batch_result = guardrail.Run(
        [topic_guardrail, nsfw_guardrail, jailbreak_guardrail], safe_content
    )
    print(f"  Overall: {'✓' if batch_result.is_allowed else '✗'}")
    # Show individual results from metadata
    if batch_result.metadata and "text_results" in batch_result.metadata:
        text_result = batch_result.metadata["text_results"][0]
        guardrail_names = ["topic", "nsfw", "jailbreak"]
        for i, result in enumerate(text_result["results"]):
            print(f"  {guardrail_names[i]}: {'✓' if result.is_allowed else '✗'}")

    # Batch execution with early return
    print("Testing batch execution with early return:")
    early_result = guardrail.Run(
        [topic_guardrail, nsfw_guardrail, jailbreak_guardrail],
        risky_content,
        early_return=True,
    )
    print(f"  Overall: {'✓' if early_result.is_allowed else '✗'}")
    # Show how many guardrails were processed
    if early_result.metadata and "text_results" in early_result.metadata:
        text_result = early_result.metadata["text_results"][0]
        processed_count = len(text_result["results"])
        print(
            f"  Guardrails processed: {processed_count} (may stop early if any fails)"
        )
        guardrail_names = ["topic", "nsfw", "jailbreak"]
        for i, result in enumerate(text_result["results"]):
            status = "✓" if result.is_allowed else "✗"
            print(f"  {guardrail_names[i]}: {status}")

    print()
    print("🎉 DSPy Guardrails is working correctly!")
    print()
    print("Key API patterns:")
    print("  guardrail.configure(lm=your_lm)  # Configure DSPy")
    print("  guardrail.Topic(topic_scopes=[...])  # Create guardrails")
    print(
        "  guardrail.Run([gr1, gr2, gr3], text)  # Bulk execution (returns aggregated result)"
    )
    print("  guardrail.Run(guardrail, text)  # Single guardrail execution")
    print("  guardrail.Run(guardrail, [text1, text2])  # Multiple texts (aggregated)")
    print("  guardrail.check('text')  # Individual check (legacy)")
    print(
        "  guardrail.Run([gr1, gr2], text, early_return=True)  # Batch with early return"
    )


if __name__ == "__main__":
    main()
