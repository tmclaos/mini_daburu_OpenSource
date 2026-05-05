from __future__ import annotations

from abc import ABC, abstractmethod

from agent_os.schemas import ActionRequest, Goal, Observation


class Skill(ABC):
    name: str
    description: str

    @abstractmethod
    def can_handle(self, goal: Goal) -> float:
        """Return confidence from 0.0 to 1.0."""

    @abstractmethod
    def plan(self, goal: Goal, observation: Observation) -> list[ActionRequest]:
        """Return tool actions."""
