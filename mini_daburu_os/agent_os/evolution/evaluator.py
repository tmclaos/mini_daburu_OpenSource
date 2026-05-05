from __future__ import annotations

from typing import Any

class EvolutionEvaluator:
    """Evaluates whether to accept or discard a proposed improvement."""

    def evaluate(self, old_metrics: dict[str, Any], new_metrics: dict[str, Any]) -> bool:
        """
        Compare the old and new version.
        Return True if new version should be accepted, False to discard.
        """
        old_rate = old_metrics.get("success_rate", 0.0)
        new_rate = new_metrics.get("success_rate", 0.0)

        # Simple Natural Selection logic
        if new_rate > old_rate:
            return True

        # Tie-breaker logic (e.g. fewer steps) could go here.
        if new_rate == old_rate:
            old_steps = old_metrics.get("steps_taken", float('inf'))
            new_steps = new_metrics.get("steps_taken", float('inf'))
            if new_steps < old_steps:
                return True

        return False
