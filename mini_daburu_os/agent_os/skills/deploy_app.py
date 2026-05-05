from __future__ import annotations

import re

from agent_os.schemas import ActionRequest, Goal, Observation
from agent_os.skills.base import Skill


class DeployAppSkill(Skill):
    name = "deploy_app"
    description = "Plan deployments to hosting providers."

    def can_handle(self, goal: Goal) -> float:
        text = goal.description.lower()
        return 0.9 if "deploy" in text else 0.0

    def plan(self, goal: Goal, observation: Observation) -> list[ActionRequest]:
        text = goal.description.lower()
        provider = "vercel"
        for candidate in ("vercel", "railway", "render"):
            if candidate in text:
                provider = candidate
                break
        project_dir = self._project_dir(goal.description)
        return [
            ActionRequest("deploy", "plan", {"provider": provider, "project_dir": project_dir}, "Plan deployment."),
            ActionRequest("files", "exists", {"path": project_dir}, "Verify project directory exists."),
        ]

    @staticmethod
    def _project_dir(text: str) -> str:
        match = re.search(r"(?:deploy|from)\s+([./\\\w-]+)", text, re.I)
        return match.group(1) if match else "."
