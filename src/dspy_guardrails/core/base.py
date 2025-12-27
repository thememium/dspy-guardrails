"""Base classes and interfaces for DSPy Guardrails."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dspy_guardrails.core.config import GuardrailConfig


@dataclass
class GuardrailResult:
    """Result of a guardrail check operation.

    Attributes:
        is_allowed: Whether the content passed the guardrail check
        reason: Optional reason for the decision
        metadata: Additional information from the guardrail check
        guardrail_name: Name of the guardrail that performed the check
    """

    is_allowed: bool
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    guardrail_name: str = ""

    def __post_init__(self):
        """Validate the result after initialization."""
        if not isinstance(self.is_allowed, bool):
            raise ValueError("is_allowed must be a boolean")
        if self.metadata is None:
            self.metadata = {}


class BaseGuardrail(ABC):
    """Abstract base class for all guardrail implementations.

    This class defines the common interface that all guardrails must implement.
    """

    def __init__(self, config: GuardrailConfig):
        """Initialize the guardrail with configuration.

        Args:
            config: Configuration object for this guardrail
        """
        self.config = config
        self._configure_dspy()

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this guardrail."""
        pass

    @abstractmethod
    def _configure_dspy(self) -> None:
        """Configure DSPy for this guardrail.

        This method should set up the DSPy language model and any other
        DSPy-specific configuration needed for this guardrail.
        """
        pass

    @abstractmethod
    def check(self, input_text: str) -> GuardrailResult:
        """Check if the input text passes this guardrail.

        Args:
            input_text: The text content to check

        Returns:
            GuardrailResult indicating whether the content is allowed
        """
        pass

    def check_batch(self, input_texts: List[str]) -> List[GuardrailResult]:
        """Check multiple input texts against this guardrail.

        Args:
            input_texts: List of text content to check

        Returns:
            List of GuardrailResult objects, one for each input
        """
        return [self.check(text) for text in input_texts]

    def __repr__(self) -> str:
        """Return a string representation of the guardrail."""
        return f"{self.__class__.__name__}(config={self.config})"
