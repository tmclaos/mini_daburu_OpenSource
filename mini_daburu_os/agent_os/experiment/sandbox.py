from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

class ExperimentRunner:
    """Safely tests improvements in a sandboxed environment."""

    def __init__(self, workspace: str = ".", experiments_dir: str = "experiments") -> None:
        self.workspace = Path(workspace).resolve()
        self.experiments_dir = self.workspace / experiments_dir
        self.experiments_dir.mkdir(parents=True, exist_ok=True)

    def run_experiment(self, proposal: dict[str, Any], target_file_path: str) -> dict[str, Any]:
        """
        Creates an isolated directory, copies the target file, applies simulated
        modifications, and returns simulated test results.
        """
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"
        exp_path = self.experiments_dir / exp_id
        exp_path.mkdir(parents=True, exist_ok=True)

        # Save the proposal
        with (exp_path / "proposal.json").open("w", encoding="utf-8") as f:
            json.dump(proposal, f, indent=2)

        source_file = self.workspace / target_file_path
        if not source_file.exists():
            return {"success": False, "error": f"Target file {target_file_path} not found."}

        target_file = exp_path / source_file.name
        shutil.copy2(source_file, target_file)

        # In a real scenario, an LLM would modify the target_file here.
        # We append a simple comment to simulate a modification.
        with target_file.open("a", encoding="utf-8") as f:
            f.write(f"\n# Modified for {exp_id}: {proposal.get('change')}\n")

        # Simulate running controlled test tasks
        # In reality, this would spin up a new AgentOS instance with the modified skill.
        test_results = {
            "exp_id": exp_id,
            "success_rate": 0.95,  # Simulated improvement
            "steps_taken": 4,
            "failures": 0,
            "verification_confidence": 0.99,
            "modified_file": str(target_file)
        }

        with (exp_path / "test_results.json").open("w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2)

        return test_results
