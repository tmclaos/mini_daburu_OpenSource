from __future__ import annotations

from abc import ABC, abstractmethod

from agent_os.schemas import ActionResult, PermissionLevel


class Tool(ABC):
    name: str
    description: str
    permission_level: PermissionLevel = PermissionLevel.SAFE

    @abstractmethod
    async def run(self, operation: str, **params) -> ActionResult:
        """Execute an operation."""
