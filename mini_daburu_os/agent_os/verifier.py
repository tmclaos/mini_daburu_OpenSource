from __future__ import annotations

from agent_os.schemas import ActionResult, Goal, VerificationResult


class Verifier:
    """Reality checker. The agent only says done when verification passes."""

    def verify(self, goal: Goal, results: list[ActionResult]) -> VerificationResult:
        if not results:
            return VerificationResult(False, "No actions were executed.")

        if any(result.requires_human for result in results):
            checkpoints = [result.checkpoint for result in results if result.requires_human]
            return VerificationResult(False, "Human checkpoint required.", {"checkpoints": checkpoints})

        if all(result.success for result in results):
            return VerificationResult(True, "All planned actions succeeded.", {"result_count": len(results)})

        errors = [result.error for result in results if result.error]
        return VerificationResult(False, "One or more actions failed.", {"errors": errors})
