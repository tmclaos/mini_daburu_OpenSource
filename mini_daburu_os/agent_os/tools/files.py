from __future__ import annotations

from pathlib import Path

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool


class FileTool(Tool):
    name = "files"
    description = "Read, write, list, and inspect files inside a workspace."

    def __init__(self, root: str = ".") -> None:
        self.root = Path(root).resolve()

    async def run(self, operation: str, **params) -> ActionResult:
        try:
            if operation == "read":
                path = self._safe_path(params["path"])
                return ActionResult(True, output=path.read_text("utf-8"))
            if operation == "write":
                path = self._safe_path(params["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(params.get("content", ""), encoding="utf-8")
                return ActionResult(True, output={"path": str(path)})
            if operation == "list":
                path = self._safe_path(params.get("path", "."))
                items = [
                    {"name": child.name, "type": "dir" if child.is_dir() else "file"}
                    for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
                ]
                return ActionResult(True, output=items)
            if operation == "exists":
                path = self._safe_path(params["path"])
                return ActionResult(True, output={"exists": path.exists(), "path": str(path)})
            return ActionResult(False, error=f"Unknown files operation: {operation}")
        except Exception as exc:
            return ActionResult(False, error=str(exc))

    def _safe_path(self, path: str) -> Path:
        target = (self.root / path).resolve()
        if self.root not in target.parents and target != self.root:
            raise ValueError(f"Path escapes workspace: {path}")
        return target
