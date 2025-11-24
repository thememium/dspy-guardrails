"""Topic compliance guardrail implementation."""

from typing import List, Optional

import dspy

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult
from dspy_guardrails.core.config import TopicGuardrailConfig
from dspy_guardrails.utils.dspy_config import configure_dspy_from_config


class GuardrailsTopicSignature(dspy.Signature):
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


class TopicGuardrail(BaseGuardrail):
    """Guardrail for checking if content stays within defined business topics."""

    def __init__(self, config: TopicGuardrailConfig):
        """Initialize the topic guardrail.

        Args:
            config: Configuration for the topic guardrail
        """
        super().__init__(config)
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
        try:
            result = self._program(
                business_scopes=self.config.business_scopes,
                competitor_names=self.config.competitor_names,
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
                    "business_scopes": self.config.business_scopes,
                    "competitor_names": self.config.competitor_names,
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
