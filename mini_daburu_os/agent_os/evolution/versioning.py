from __future__ import annotations

import shutil
import re
from pathlib import Path

class VersioningManager:
    """Manages versioning for skills after successful evolution."""

    def __init__(self, workspace: str = ".", skills_dir: str = "agent_os/skills") -> None:
        self.workspace = Path(workspace).resolve()
        self.skills_dir = self.workspace / skills_dir

    def promote(self, source_file_path: str, target_filename: str) -> str:
        """
        Promotes a file from an experiment to production by giving it a version number.
        Returns the path to the newly promoted file.
        """
        source_path = Path(source_file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file {source_path} does not exist.")

        base_name = Path(target_filename).stem
        ext = Path(target_filename).suffix

        # Find next version number
        existing_versions = list(self.skills_dir.glob(f"{base_name}_v*{ext}"))
        next_version = 1

        if existing_versions:
            highest_v = 0
            for f in existing_versions:
                match = re.search(r"_v(\d+)", f.name)
                if match:
                    v = int(match.group(1))
                    highest_v = max(highest_v, v)
            next_version = highest_v + 1

        new_filename = f"{base_name}_v{next_version}{ext}"
        new_filepath = self.skills_dir / new_filename

        shutil.copy2(source_path, new_filepath)
        return str(new_filepath)
