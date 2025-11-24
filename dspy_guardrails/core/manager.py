"""Guardrail manager for orchestrating multiple guardrails."""

from typing import Dict, List, Optional

from dspy_guardrails.core.base import BaseGuardrail, GuardrailResult


class GuardrailManager:
    """Manager class for orchestrating multiple guardrails.

    This class allows you to register multiple guardrails and run them
    against input text, aggregating the results.
    """

    def __init__(self):
        """Initialize the guardrail manager."""
        self._guardrails: Dict[str, BaseGuardrail] = {}

    def add_guardrail(self, name: str, guardrail: BaseGuardrail) -> None:
        """Add a guardrail to the manager.

        Args:
            name: Unique name for the guardrail
            guardrail: The guardrail instance to add

        Raises:
            ValueError: If a guardrail with the same name already exists
        """
        if name in self._guardrails:
            raise ValueError(f"Guardrail with name '{name}' already exists")
        self._guardrails[name] = guardrail

    def remove_guardrail(self, name: str) -> None:
        """Remove a guardrail from the manager.

        Args:
            name: Name of the guardrail to remove

        Raises:
            KeyError: If the guardrail doesn't exist
        """
        if name not in self._guardrails:
            raise KeyError(f"Guardrail '{name}' not found")
        del self._guardrails[name]

    def get_guardrail(self, name: str) -> BaseGuardrail:
        """Get a guardrail by name.

        Args:
            name: Name of the guardrail

        Returns:
            The guardrail instance

        Raises:
            KeyError: If the guardrail doesn't exist
        """
        if name not in self._guardrails:
            raise KeyError(f"Guardrail '{name}' not found")
        return self._guardrails[name]

    def list_guardrails(self) -> List[str]:
        """List all registered guardrail names.

        Returns:
            List of guardrail names
        """
        return list(self._guardrails.keys())

    def check(
        self, input_text: str, guardrail_names: Optional[List[str]] = None
    ) -> Dict[str, GuardrailResult]:
        """Check input text against specified guardrails.

        Args:
            input_text: The text to check
            guardrail_names: List of guardrail names to run. If None, runs all guardrails.

        Returns:
            Dictionary mapping guardrail names to their results
        """
        if guardrail_names is None:
            guardrail_names = self.list_guardrails()

        results = {}
        for name in guardrail_names:
            if name not in self._guardrails:
                raise KeyError(f"Guardrail '{name}' not found")
            results[name] = self._guardrails[name].check(input_text)

        return results

    def check_batch(
        self, input_texts: List[str], guardrail_names: Optional[List[str]] = None
    ) -> Dict[str, List[GuardrailResult]]:
        """Check multiple input texts against specified guardrails.

        Args:
            input_texts: List of texts to check
            guardrail_names: List of guardrail names to run. If None, runs all guardrails.

        Returns:
            Dictionary mapping guardrail names to lists of their results
        """
        if guardrail_names is None:
            guardrail_names = self.list_guardrails()

        results = {}
        for name in guardrail_names:
            if name not in self._guardrails:
                raise KeyError(f"Guardrail '{name}' not found")
            results[name] = self._guardrails[name].check_batch(input_texts)

        return results

    def check_all_allowed(
        self, input_text: str, guardrail_names: Optional[List[str]] = None
    ) -> bool:
        """Check if input text passes all specified guardrails.

        Args:
            input_text: The text to check
            guardrail_names: List of guardrail names to run. If None, runs all guardrails.

        Returns:
            True if all guardrails allow the content, False otherwise
        """
        results = self.check(input_text, guardrail_names)
        return all(result.is_allowed for result in results.values())

    def get_blocking_reasons(
        self, input_text: str, guardrail_names: Optional[List[str]] = None
    ) -> List[str]:
        """Get reasons why input text was blocked by guardrails.

        Args:
            input_text: The text to check
            guardrail_names: List of guardrail names to run. If None, runs all guardrails.

        Returns:
            List of blocking reasons from guardrails that rejected the content
        """
        results = self.check(input_text, guardrail_names)
        reasons = []
        for name, result in results.items():
            if not result.is_allowed and result.reason:
                reasons.append(f"{name}: {result.reason}")
        return reasons

    def __len__(self) -> int:
        """Return the number of registered guardrails."""
        return len(self._guardrails)

    def __contains__(self, name: str) -> bool:
        """Check if a guardrail is registered."""
        return name in self._guardrails

    def __repr__(self) -> str:
        """Return a string representation of the manager."""
        guardrail_names = self.list_guardrails()
        return f"GuardrailManager(guardrails={guardrail_names})"
