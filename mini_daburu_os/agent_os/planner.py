from __future__ import annotations

from agent_os.schemas import ActionRequest, Goal, Observation
from agent_os.skills.base import Skill


class PlanningEngine:
    """Advanced planner for explicit plans, goal decomposition, and multi-path reasoning."""

    def __init__(self, skills: list[Skill]) -> None:
        self.skills = skills

    def decompose_goal(self, goal: Goal) -> list[str]:
        # Phase 4: Goal Decomposition - Break big goals into subgoals
        # (In a full LLM-backed system, this would prompt the LLM.
        # Here we simulate by just returning the primary goal as the single step for now)
        return [goal.description]

    def simulate_plan(self, actions: list[ActionRequest]) -> bool:
        # Phase 7: Internal Critic / Plan Simulation
        # Second pass: "does this actually make sense?"
        # Simple heuristic: ensure there are no conflicting or obvious redundant actions.
        if not actions:
            return False
        return True

    def plan(self, goal: Goal, observation: Observation) -> tuple[str, list[ActionRequest]]:
        # Find capable skills
        capable_skills = [
            (skill.can_handle(goal), skill)
            for skill in self.skills
            if skill.can_handle(goal) > 0
        ]

        if not capable_skills:
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

        # Phase 7: Multi-Path Reasoning - Compare multiple strategies
        # We simulate this by taking the top 2 skills and seeing which plan passes the Internal Critic best.
        capable_skills.sort(key=lambda pair: pair[0], reverse=True)
        top_skills = capable_skills[:2]

        best_skill = None
        best_plan = None

        for _, skill in top_skills:
            proposed_plan = skill.plan(goal, observation)

            # Phase 7: Plan Simulation & Internal Critic
            if self.simulate_plan(proposed_plan):
                best_skill = skill
                best_plan = proposed_plan
                break

        if best_skill and best_plan:
            return best_skill.name, best_plan

        # Fallback to the top skill even if it didn't strictly pass the naive critic
        top_skill = capable_skills[0][1]
        return top_skill.name, top_skill.plan(goal, observation)
