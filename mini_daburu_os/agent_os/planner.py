from __future__ import annotations

from agent_os.schemas import ActionRequest, Goal, Observation
from agent_os.skills.base import Skill


class Planner:
    """Tiny planner: pick the best skill or ask the human for direction."""

    def __init__(self, skills: list[Skill]) -> None:
        self.skills = skills

    def plan(self, goal: Goal, observation: Observation) -> tuple[str, list[ActionRequest]]:
        scored = sorted(
            ((skill.can_handle(goal), skill) for skill in self.skills),
            key=lambda pair: pair[0],
            reverse=True,
        )
        if scored and scored[0][0] > 0:
            skill = scored[0][1]
            return skill.name, skill.plan(goal, observation)
        return (
            "ask_human",
            [
                ActionRequest(
                    "human",
                    "ask",
                    {"question": f"I do not have a skill for this yet: {goal.description}\nWhat should I try first?"},
                    "Unknown goal; ask for a first move.",
                )
            ],
        )
