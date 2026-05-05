from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from agent_os.schemas import ActionRequest, ActionResult, Goal, Observation


class TraceLogger:
    """Full step-by-step trace logger for Phase 1 Logging System."""

    def __init__(self, log_path: str = "data/trace.jsonl") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, data: dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "data": data
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def log_goal_started(self, goal: Goal) -> None:
        self.log_event("goal_started", goal.to_dict())

    def log_observation(self, observation: Observation) -> None:
        self.log_event("observation", {"summary": observation.summary, "data": observation.data})

    def log_plan(self, skill_name: str, actions: list[ActionRequest]) -> None:
        self.log_event("plan_generated", {
            "skill": skill_name,
            "actions": [a.__dict__ for a in actions]
        })

    def log_action_started(self, action: ActionRequest) -> None:
        self.log_event("action_started", action.__dict__)

    def log_action_result(self, result: ActionResult) -> None:
        self.log_event("action_result", result.to_dict())

    def log_goal_completed(self, goal: Goal, success: bool, reason: str) -> None:
        self.log_event("goal_completed", {
            "goal_id": goal.goal_id,
            "success": success,
            "reason": reason
        })
