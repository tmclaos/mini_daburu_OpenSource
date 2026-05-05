from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from enum import Enum


def new_id() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Goal:
    description: str
    goal_id: str = field(default_factory=new_id)
    status: str = "active"
    created_at: str = field(default_factory=now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ActionRequest:
    tool: str
    operation: str
    params: dict[str, Any] = field(default_factory=dict)
    reason: str = ""

@dataclass
class ActionResult:
    success: bool
    output: Any = None
    error: str = ""
    requires_human: bool = False
    checkpoint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class PermissionLevel(str, Enum):
    SAFE = "SAFE"
    LIMITED = "LIMITED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class State:
    goal: Goal | None = None
    plan: list[str] = field(default_factory=list)
    last_action: ActionRequest | None = None
    last_result: ActionResult | None = None
    blockers: list[str] = field(default_factory=list)

@dataclass
class Experience:
    lesson: str
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Observation:
    summary: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    success: bool
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class Episode:
    goal: Goal
    observation: Observation
    actions: list[ActionRequest]
    results: list[ActionResult]
    verification: VerificationResult
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal.to_dict(),
            "observation": asdict(self.observation),
            "actions": [asdict(action) for action in self.actions],
            "results": [result.to_dict() for result in self.results],
            "verification": asdict(self.verification),
            "created_at": self.created_at,
        }
