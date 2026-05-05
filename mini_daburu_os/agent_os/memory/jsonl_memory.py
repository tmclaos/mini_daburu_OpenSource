from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonlMemory:
    """Tiny append-only memory store."""

    def __init__(self, path: str = "data/episodes.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, item: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(item, separators=(",", ":"), default=str) + "\n")

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = [line for line in self.path.read_text("utf-8").splitlines() if line.strip()]
        return [json.loads(line) for line in lines[-limit:]]

    def search(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        needle = text.lower()
        hits = []
        for item in reversed(self.recent(limit=1000)):
            haystack = json.dumps(item, default=str).lower()
            if needle in haystack:
                hits.append(item)
            if len(hits) >= limit:
                break
        return hits


class ReflectionMemory(JsonlMemory):
    """Tiny append-only memory store for reflections."""

    def __init__(self, path: str = "data/reflections.jsonl") -> None:
        super().__init__(path)
