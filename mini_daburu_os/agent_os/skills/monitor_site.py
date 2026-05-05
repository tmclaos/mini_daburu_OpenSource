from __future__ import annotations

import re

from agent_os.schemas import ActionRequest, Goal, Observation
from agent_os.skills.base import Skill


class MonitorSiteSkill(Skill):
    name = "monitor_site"
    description = "Check uptime for a website."

    def can_handle(self, goal: Goal) -> float:
        text = goal.description.lower()
        if "uptime" in text or "monitor" in text or "check" in text:
            return 0.75
        return 0.0

    def plan(self, goal: Goal, observation: Observation) -> list[ActionRequest]:
        url = self._url(goal.description)
        return [ActionRequest("monitor", "uptime", {"url": url}, "Check live HTTP status.")]

    @staticmethod
    def _url(text: str) -> str:
        match = re.search(r"https?://\S+", text)
        if match:
            return match.group(0)
        domain = re.search(r"\b([a-z0-9.-]+\.[a-z]{2,})\b", text, re.I)
        return f"https://{domain.group(1)}" if domain else "https://example.com"
