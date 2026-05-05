from __future__ import annotations

import aiohttp
from typing import Any

from agent_os.schemas import ActionResult, PermissionLevel
from agent_os.tools.base import Tool


class APITool(Tool):
    name = "api"
    description = "External Integration: HTTP requests to external APIs."
    permission_level = PermissionLevel.LIMITED

    def __init__(self) -> None:
        pass

    async def run(self, operation: str, **params) -> ActionResult:
        if operation not in ["get", "post", "put", "delete", "patch"]:
            return ActionResult(success=False, error=f"Unsupported operation: {operation}")

        url = params.get("url")
        if not url:
            return ActionResult(success=False, error="URL is required")

        headers = params.get("headers", {})
        data = params.get("data", None)
        json_data = params.get("json", None)

        try:
            async with aiohttp.ClientSession() as session:
                method = getattr(session, operation)
                async with method(url, headers=headers, data=data, json=json_data) as response:
                    text = await response.text()
                    try:
                        output = await response.json()
                    except Exception:
                        output = text

                    if response.status >= 400:
                        return ActionResult(
                            success=False,
                            error=f"HTTP {response.status}: {text}",
                            output={"status": response.status, "body": output}
                        )

                    return ActionResult(
                        success=True,
                        output={"status": response.status, "body": output}
                    )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
