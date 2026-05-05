from __future__ import annotations

from agent_os.schemas import ActionRequest, ActionResult
from agent_os.tools.base import Tool


class ToolRegistry:
    """Spinal cord for tools: name -> callable capability."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

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
        return await tool.run(request.operation, **request.params)
