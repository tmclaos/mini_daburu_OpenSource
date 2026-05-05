from __future__ import annotations

from typing import Any
from agent_os.schemas import Episode

class ReflectionGenerator:
    """Generates a structured reflection from an episode."""

    def generate(self, episode: Episode) -> dict[str, Any]:
        success = episode.verification.success
        failures = [r.error for r in episode.results if r.error]

        # Simple heuristic for inefficiencies/tool misuse for the minimal implementation
        inefficiencies = []
        if len(episode.actions) > 5 and not success:
            inefficiencies.append("Too many actions without success.")

        tool_misuse = []
        if any("not found" in str(r.error).lower() for r in episode.results):
            tool_misuse.append("Attempted to use tools incorrectly or missing dependencies.")

        what_should_change = []
        if not success:
            what_should_change.append("Improve skill planning or add verification step.")

        return {
            "goal": episode.goal.description,
            "success": success,
            "failures": failures,
            "inefficiencies": inefficiencies,
            "tool_misuse": tool_misuse,
            "what_should_change": what_should_change
        }
