from __future__ import annotations

from typing import Any

class ImprovementProposer:
    """Proposes improvements based on a reflection."""

    def propose(self, reflection: dict[str, Any]) -> dict[str, Any] | None:
        """
        Reads a reflection and generates a structured improvement proposal.
        Returns None if no improvements are deemed necessary.
        """
        if reflection.get("success", True) and not reflection.get("inefficiencies") and not reflection.get("tool_misuse"):
            return None

        # Simple logic to generate a proposal based on the reflection
        proposals = []

        if reflection.get("failures"):
            proposals.append({
                "type": "skill",
                "target": "unknown_skill",  # In a real system, would determine the exact skill
                "change": "Fix errors that led to failure.",
                "expected_benefit": "Prevent failure on similar tasks.",
                "test_plan": "Run a similar task and check if it succeeds."
            })

        if reflection.get("tool_misuse"):
            proposals.append({
                "type": "tool_usage",
                "target": "tool_planning",
                "change": "Ensure tools are used with correct parameters and existing dependencies.",
                "expected_benefit": "Avoid tool errors.",
                "test_plan": "Execute task verifying correct tool usage."
            })

        if reflection.get("inefficiencies"):
            proposals.append({
                "type": "strategy",
                "target": "planner",
                "change": "Optimize action sequence to reduce steps.",
                "expected_benefit": "Faster execution.",
                "test_plan": "Run a task and verify step count is reduced."
            })

        if not proposals:
            return {
                 "type": "strategy",
                 "target": "general",
                 "change": "Review planning strategy.",
                 "expected_benefit": "Better success rate.",
                 "test_plan": "Run previous task again."
            }

        return proposals[0]  # Return the highest priority proposal for now
