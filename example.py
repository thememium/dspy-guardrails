#!/usr/bin/env python3
"""Example usage of the DSPy Guardrails package."""

from dspy_guardrails import (JailbreakGuardrail, KeywordsGuardrail,
                             NsfwGuardrail, PiiGuardrail, SecretKeysGuardrail,
                             TopicGuardrail)
from dspy_guardrails.core.config import (JailbreakGuardrailConfig,
                                         KeywordsGuardrailConfig,
                                         NsfwGuardrailConfig,
                                         PiiGuardrailConfig,
                                         SecretKeysGuardrailConfig,
                                         TopicGuardrailConfig)


def main():
    print("DSPy Guardrails Package Example")
    print("=" * 40)

    # Show all available guardrails
    import dspy_guardrails

    guardrail_classes = [
        name for name in dspy_guardrails.__all__ if name.endswith("Guardrail")
    ]
    print(f"Available guardrails: {', '.join(guardrail_classes)}")
    print()

    # Create examples of different guardrails
    guardrails = []

    # Topic guardrail
    topic_config = TopicGuardrailConfig(
        business_scopes=["Shipping Software", "Logistics", "Package Delivery"],
        competitor_names=["Shipo", "FastShip", "QuickDeliver"],
    )
    topic_guardrail = TopicGuardrail(topic_config)
    guardrails.append(topic_guardrail)

    # NSFW guardrail
    nsfw_config = NsfwGuardrailConfig(sensitivity_level="medium")
    nsfw_guardrail = NsfwGuardrail(nsfw_config)
    guardrails.append(nsfw_guardrail)

    # Jailbreak guardrail
    jailbreak_config = JailbreakGuardrailConfig(detection_threshold=0.8)
    jailbreak_guardrail = JailbreakGuardrail(jailbreak_config)
    guardrails.append(jailbreak_guardrail)

    # PII guardrail
    pii_config = PiiGuardrailConfig()
    pii_guardrail = PiiGuardrail(pii_config)
    guardrails.append(pii_guardrail)

    # Keywords guardrail
    keywords_config = KeywordsGuardrailConfig(
        blocked_keywords=["inappropriate", "offensive"]
    )
    keywords_guardrail = KeywordsGuardrail(keywords_config)
    guardrails.append(keywords_guardrail)

    # Secret keys guardrail
    secret_keys_config = SecretKeysGuardrailConfig()
    secret_keys_guardrail = SecretKeysGuardrail(secret_keys_config)
    guardrails.append(secret_keys_guardrail)

    for guardrail in guardrails:
        print(f"✓ {guardrail.name} guardrail initialized")

    print()
    print("Package structure is working correctly!")
    print("To use the guardrails, you would call:")
    print("  result = guardrail.check('Your text here')")
    print("  print(f'Allowed: {result.is_allowed}, Reason: {result.reason}')")
    print()

    # Demonstrate factory functions
    print("Factory Functions Example:")
    from dspy_guardrails import create_nsfw_guardrail, create_topic_guardrail

    easy_topic = create_topic_guardrail(
        business_scopes=["AI", "Machine Learning"],
        competitor_names=["OpenAI", "Google"],
    )
    easy_nsfw = create_nsfw_guardrail(sensitivity_level="high")

    print(f"Easy topic guardrail: {easy_topic.name}")
    print(f"Easy NSFW guardrail: {easy_nsfw.name}")

    # Demonstrate GuardrailManager
    print("\nGuardrailManager Example:")
    from dspy_guardrails import GuardrailManager

    manager = GuardrailManager()
    manager.add_guardrail("topic", topic_guardrail)
    manager.add_guardrail("nsfw", nsfw_guardrail)

    print(f"Manager has {len(manager)} guardrails: {manager.list_guardrails()}")

    # Check if all guardrails pass
    all_pass = manager.check_all_allowed(
        "This is a safe message about shipping logistics"
    )
    print(f"All guardrails pass for safe content: {all_pass}")

    # Get blocking reasons for problematic content
    reasons = manager.get_blocking_reasons("This contains bad content")
    print(f"Blocking reasons: {reasons}")


if __name__ == "__main__":
    main()
