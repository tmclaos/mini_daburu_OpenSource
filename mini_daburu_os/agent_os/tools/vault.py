from __future__ import annotations

import base64
import json
from pathlib import Path

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool


class VaultTool(Tool):
    name = "vault"
    description = "Local development secret store. Replace for production."

    def __init__(self, path: str = "data/vault.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def run(self, operation: str, **params) -> ActionResult:
        data = self._load()
        if operation == "set":
            key = params["key"]
            data[key] = self._encode(params.get("value", ""))
            self._save(data)
            return ActionResult(True, output={"key": key, "stored": True})
        if operation == "get":
            key = params["key"]
            if key not in data:
                return ActionResult(False, error=f"Secret not found: {key}")
            return ActionResult(True, output={"key": key, "value": self._decode(data[key])})
        if operation == "list":
            return ActionResult(True, output={"keys": sorted(data)})
        if operation == "delete":
            data.pop(params["key"], None)
            self._save(data)
            return ActionResult(True, output={"deleted": params["key"]})
        return ActionResult(False, error=f"Unknown vault operation: {operation}")

    def _load(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text("utf-8"))

    def _save(self, data: dict[str, str]) -> None:
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    @staticmethod
    def _encode(value: str) -> str:
        return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii")

    @staticmethod
    def _decode(value: str) -> str:
        return base64.urlsafe_b64decode(value.encode("ascii")).decode("utf-8")
