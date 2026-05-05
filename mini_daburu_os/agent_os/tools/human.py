from __future__ import annotations

import asyncio

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool


class HumanTool(Tool):
    name = "human"
    description = "Ask the human for missing information or verification checkpoints."

    async def run(self, operation: str, **params) -> ActionResult:
        if operation != "ask":
            return ActionResult(False, error=f"Unknown human operation: {operation}")
        question = params.get("question", "Input needed:")
        answer = await asyncio.to_thread(input, f"{question}\n> ")
        return ActionResult(True, output={"answer": answer})
