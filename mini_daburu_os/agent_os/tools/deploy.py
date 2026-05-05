from __future__ import annotations

import shutil

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool


class DeployTool(Tool):
    name = "deploy"
    description = "Plan or execute deployments with provider CLIs."

    async def run(self, operation: str, **params) -> ActionResult:
        provider = params.get("provider", "vercel").lower()
        project_dir = params.get("project_dir", ".")
        execute = bool(params.get("execute", False))
        command = self._command(provider, project_dir)
        if operation == "plan":
            return ActionResult(True, output={"provider": provider, "project_dir": project_dir, "command": command})
        if operation == "deploy":
            if not execute:
                return ActionResult(True, output={"dry_run": True, "command": command})
            if not shutil.which(command[0]):
                return ActionResult(False, error=f"{command[0]} CLI is not installed.")
            return ActionResult(
                False,
                requires_human=True,
                checkpoint="deployment_execution",
                error="Deployment execution is intentionally delegated to ShellTool or a human-approved command.",
            )
        return ActionResult(False, error=f"Unknown deploy operation: {operation}")

    @staticmethod
    def _command(provider: str, project_dir: str) -> list[str]:
        if provider == "vercel":
            return ["vercel", "--yes", "--cwd", project_dir]
        if provider == "railway":
            return ["railway", "up"]
        if provider == "render":
            return ["render", "deploy"]
        raise ValueError(f"Unsupported provider: {provider}")
