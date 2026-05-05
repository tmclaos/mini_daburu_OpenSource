from __future__ import annotations

import urllib.request
import urllib.error
from agent_os.schemas import ActionResult, Goal, VerificationResult, AgentState


class Verifier:
    """Reality checker. The agent only says done when verification passes."""

    def verify(self, goal: Goal, state: AgentState, results: list[ActionResult]) -> VerificationResult:
        if not results:
            return VerificationResult(False, "No actions were executed.")

        if "deploy" in goal.description.lower():
            if not self.check_url_live(state):
                return VerificationResult(False, "Deployment URL is not live.", {"url": state.last_result.output.get("url") if state.last_result and isinstance(state.last_result.output, dict) else None})
        elif "account" in goal.description.lower():
            if not self.check_logged_in(state):
                return VerificationResult(False, "Account login check failed.")

        if any(result.requires_human for result in results):
            checkpoints = [result.checkpoint for result in results if result.requires_human]
            return VerificationResult(False, "Human checkpoint required.", {"checkpoints": checkpoints})

        if all(result.success for result in results):
            return VerificationResult(True, "All planned actions succeeded.", {"result_count": len(results)})

        errors = [result.error for result in results if result.error]
        return VerificationResult(False, "One or more actions failed.", {"errors": errors})


    def check_url_live(self, state: AgentState) -> bool:
        if not state.last_result or not isinstance(state.last_result.output, dict):
            return False
        url = state.last_result.output.get("url")
        if not url:
            return False
        if not url.startswith("http"):
            url = f"https://{url}"
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False

    def check_logged_in(self, state: AgentState) -> bool:
        if state.blocked:
            return False
        if state.last_result and state.last_result.success:
            return True
        return False
