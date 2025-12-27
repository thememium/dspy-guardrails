"""Topic compliance guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import TopicGuardrailConfig
from dspy_guardrails.utils.dspy_config import (
    configure_dspy_from_config,
    is_dspy_configured,
)


class GuardrailsTopicSignature(dspy.Signature):
    """You are a content analysis system that determines if text stays on topic.

    Determine if the text stays within the defined topic scope. Flag any content that strays from the allowed topics."""

    topic_scopes: List[str] = dspy.InputField(
        desc="The defined topic scope or topics. A list of topics that are considered on topic."
    )
    blocked_topics: List[str] = dspy.InputField(
        desc="List of blocked topics or items to flag if mentioned in the content."
    )
    user_input: str = dspy.InputField(desc="The text content to analyze.")
    off_topic_reasons: Optional[List[str]] = dspy.OutputField(
        desc="List of reasons why the content is off topic, if applicable. Empty if on topic. A single word reason is sufficient."
    )
    is_on_topic: bool = dspy.OutputField(
        desc="Boolean indicating if the content stays on topic. True if on topic, False if off topic."
    )


class TopicGuardrail(BaseGuardrail):
    """Guardrail for checking if content stays within defined topic scopes."""

    def __init__(self, config: TopicGuardrailConfig):
        """Initialize the topic guardrail.

        Args:
            config: Configuration for the topic guardrail
        """
        super().__init__(config)
        self.config: TopicGuardrailConfig = config  # Type hint for better type checking
        self._program = dspy.ChainOfThought(GuardrailsTopicSignature)

    @property
    def name(self) -> str:
        """Return the name of this guardrail."""
        return "topic"

    def _configure_dspy(self) -> None:
        """Configure DSPy for topic guardrail."""
        configure_dspy_from_config(self.config)

    def check(self, input_text: str) -> GuardrailResult:
        """Check if the input text stays on topic.

        Args:
            input_text: The text content to analyze

        Returns:
            GuardrailResult indicating if content is on topic
        """
        if not is_dspy_configured():
            return GuardrailResult(
                is_allowed=False,
                reason="DSPy is not properly configured. Please configure DSPy before using guardrails.",
                metadata={"error": "DSPy not configured"},
                guardrail_name=self.name,
            )

        try:
            result = self._program(
                topic_scopes=self.config.topic_scopes,
                blocked_topics=self.config.blocked_topics,
                user_input=input_text,
            )

            is_allowed = result.is_on_topic
            reason = None
            if not is_allowed and result.off_topic_reasons:
                reason = "; ".join(result.off_topic_reasons)

            return GuardrailResult(
                is_allowed=is_allowed,
                reason=reason,
                metadata={
                    "off_topic_reasons": result.off_topic_reasons or [],
                    "topic_scopes": self.config.topic_scopes,
                    "blocked_topics": self.config.blocked_topics,
                },
                guardrail_name=self.name,
            )

        except Exception as e:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Error during topic check: {str(e)}",
                metadata={"error": str(e)},
                guardrail_name=self.name,
            )
