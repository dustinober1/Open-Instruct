"""
In-memory store for learning objectives.

This is a simple in-memory implementation for the MVP. In production,
this should be replaced with a proper database-backed solution.
"""

from typing import Dict, Optional

from src.core.models import LearningObjective


class ObjectiveStore:
    """Simple in-memory store for learning objectives."""

    def __init__(self):
        """Initialize the empty objective store."""
        self._objectives: Dict[str, LearningObjective] = {}

    def add_objective(self, objective: LearningObjective) -> None:
        """
        Add an objective to the store.

        Args:
            objective: The LearningObjective to store
        """
        self._objectives[objective.id] = objective

    def add_objectives(self, objectives: list[LearningObjective]) -> None:
        """
        Add multiple objectives to the store.

        Args:
            objectives: List of LearningObjectives to store
        """
        for objective in objectives:
            self.add_objective(objective)

    def get_objective(self, objective_id: str) -> Optional[LearningObjective]:
        """
        Retrieve an objective by ID.

        Args:
            objective_id: The objective ID to retrieve (e.g., LO-001)

        Returns:
            The LearningObjective if found, None otherwise
        """
        return self._objectives.get(objective_id)

    def list_objectives(self) -> list[LearningObjective]:
        """
        List all stored objectives.

        Returns:
            List of all stored LearningObjectives
        """
        return list(self._objectives.values())

    def clear(self) -> None:
        """Clear all objectives from the store."""
        self._objectives.clear()


# Global singleton instance
_objective_store = ObjectiveStore()


def get_objective_store() -> ObjectiveStore:
    """
    Get the global objective store instance.

    Returns:
        The singleton ObjectiveStore instance
    """
    return _objective_store
