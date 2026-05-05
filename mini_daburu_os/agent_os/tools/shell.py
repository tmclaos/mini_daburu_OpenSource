from __future__ import annotations

import asyncio
import shlex
import subprocess

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool


class ShellTool(Tool):
    name = "shell"
    description = "Run allowed local commands for tests, scripts, and project tasks."

    def __init__(self, cwd: str = ".", allow_prefixes: list[list[str]] | None = None) -> None:
        self.cwd = cwd
        self.allow_prefixes = allow_prefixes or [
            ["python"],
            ["py"],
            ["pytest"],
            ["npm"],
            ["node"],
            ["git", "status"],
            ["git", "diff"],
        ]

    async def run(self, operation: str, **params) -> ActionResult:
        if operation != "run":
            return ActionResult(False, error=f"Unknown shell operation: {operation}")
        command = params.get("command", "")
        timeout = int(params.get("timeout", 120))
        argv = shlex.split(command, posix=False)
        if not argv:
            return ActionResult(False, error="No command provided.")
        if not self._allowed(argv):
            return ActionResult(False, error=f"Command not allowed by ShellTool policy: {command}")

        def _run() -> subprocess.CompletedProcess[str]:
            return subprocess.run(argv, cwd=self.cwd, capture_output=True, text=True, timeout=timeout)

        try:
            completed = await asyncio.to_thread(_run)
            return ActionResult(
                completed.returncode == 0,
                output={
                    "stdout": completed.stdout[-4000:],
                    "stderr": completed.stderr[-4000:],
                    "exit_code": completed.returncode,
                },
                error=completed.stderr[-1000:] if completed.returncode else "",
            )
        except Exception as exc:
            return ActionResult(False, error=str(exc))

    def _allowed(self, argv: list[str]) -> bool:
        lowered = [part.lower() for part in argv]
        for prefix in self.allow_prefixes:
            if lowered[: len(prefix)] == [part.lower() for part in prefix]:
                return True
        return False
