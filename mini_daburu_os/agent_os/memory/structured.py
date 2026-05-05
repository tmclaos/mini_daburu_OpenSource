from __future__ import annotations

import json
from pathlib import Path
from typing import Any

class StructuredMemory:
    """Store explicit structured knowledge like site profiles and instruction memory."""

    def __init__(self, data_dir: str = "data") -> None:
        self.profiles_path = Path(data_dir) / "site_profiles.json"
        self.instructions_path = Path(data_dir) / "instructions.json"
        self._ensure_files()

    def _ensure_files(self) -> None:
        self.profiles_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.profiles_path.exists():
            self.profiles_path.write_text("{}", encoding="utf-8")
        if not self.instructions_path.exists():
            self.instructions_path.write_text("{}", encoding="utf-8")

    def get_profile(self, site: str) -> dict[str, Any]:
        data = json.loads(self.profiles_path.read_text("utf-8"))
        return data.get(site, {})

    def save_profile(self, site: str, profile: dict[str, Any]) -> None:
        data = json.loads(self.profiles_path.read_text("utf-8"))
        data[site] = profile
        self.profiles_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_instructions(self, category: str) -> dict[str, Any]:
        data = json.loads(self.instructions_path.read_text("utf-8"))
        return data.get(category, {})

    def save_instruction(self, category: str, key: str, value: Any) -> None:
        data = json.loads(self.instructions_path.read_text("utf-8"))
        if category not in data:
            data[category] = {}
        data[category][key] = value
        self.instructions_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
