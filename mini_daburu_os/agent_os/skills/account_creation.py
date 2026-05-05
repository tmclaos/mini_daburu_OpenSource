from __future__ import annotations

import re

from agent_os.schemas import ActionRequest, Goal, Observation
from agent_os.skills.base import Skill


class AccountCreationSkill(Skill):
    name = "account_creation"
    description = "Create or resume account signup on a domain with human verification checkpoints."

    def can_handle(self, goal: Goal) -> float:
        text = goal.description.lower()
        if "account" in text and any(word in text for word in ("create", "signup", "sign up", "register")):
            return 0.95
        return 0.0

    def plan(self, goal: Goal, observation: Observation) -> list[ActionRequest]:
        domain = self._domain(goal.description)
        email = self._email(goal.description) or goal.metadata.get("email", "")
        url = domain if domain.startswith(("http://", "https://")) else f"https://{domain}"
        actions = [
            ActionRequest("browser", "navigate", {"url": url}, "Open target domain."),
            ActionRequest("browser", "click_text", {"text": "Sign up"}, "Try visible signup link."),
        ]
        if email:
            actions.append(ActionRequest("browser", "type", {"selector": 'input[type="email"]', "text": email}, "Enter owned email."))
        actions.extend(
            [
                ActionRequest("browser", "read", {}, "Read the page state."),
                ActionRequest(
                    "human",
                    "ask",
                    {
                        "question": (
                            "If the page asks for CAPTCHA, SMS, or email verification, complete it or paste the code. "
                            "What happened?"
                        )
                    },
                    "Verification gates need legitimate human/operator input.",
                ),
                ActionRequest("vault", "set", {"key": f"account_status:{domain}", "value": "created_or_pending_verification"}, "Remember account status."),
            ]
        )
        return actions

    @staticmethod
    def _domain(text: str) -> str:
        match = re.search(r"\b(?:https?://)?([a-z0-9.-]+\.[a-z]{2,})(?:/\S*)?\b", text, re.I)
        return match.group(1) if match else "example.com"

    @staticmethod
    def _email(text: str) -> str:
        match = re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", text)
        return match.group(0) if match else ""
