from __future__ import annotations

from agent_os.schemas import ActionRequest, ActionResult, PermissionLevel
from agent_os.tools.base import Tool


class ToolRegistry:
    """Spinal cord for tools: name -> callable capability."""

    def __init__(self, max_permission_level: PermissionLevel = PermissionLevel.HIGH) -> None:
        self._tools: dict[str, Tool] = {}
        self.max_permission_level = max_permission_level

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def names(self) -> list[str]:
        return sorted(self._tools)

    def describe(self) -> list[dict[str, str]]:
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]

    async def run(self, request: ActionRequest) -> ActionResult:
        tool = self._tools.get(request.tool)
        if not tool:
            return ActionResult(success=False, error=f"Unknown tool: {request.tool}")

        # Check permission
        permission_order = {
            PermissionLevel.SAFE: 0,
            PermissionLevel.LIMITED: 1,
            PermissionLevel.HIGH: 2,
            PermissionLevel.CRITICAL: 3,
        }
        if permission_order[tool.permission_level] > permission_order[self.max_permission_level]:
            return ActionResult(success=False, error=f"Permission denied: Tool {tool.name} requires {tool.permission_level} but max is {self.max_permission_level}", requires_human=True, checkpoint="permission_escalation")

        return await tool.run(request.operation, **request.params)
