from __future__ import annotations

import datetime
import json
from pathlib import Path

from agent_os.memory.jsonl_memory import JsonlMemory, ReflectionMemory
from agent_os.learning.reflection import ReflectionGenerator
from agent_os.improvement.proposer import ImprovementProposer
from agent_os.experiment.sandbox import ExperimentRunner
from agent_os.evolution.evaluator import EvolutionEvaluator
from agent_os.evolution.versioning import VersioningManager
from agent_os.planner import Planner
from agent_os.schemas import Episode, Goal, Observation, AgentState
from agent_os.skills import DEFAULT_SKILLS
from agent_os.tools.browser import BrowserTool
from agent_os.tools.deploy import DeployTool
from agent_os.tools.email_tool import EmailTool
from agent_os.tools.files import FileTool
from agent_os.tools.human import HumanTool
from agent_os.tools.monitor import MonitorTool
from agent_os.tools.registry import ToolRegistry
from agent_os.tools.shell import ShellTool
from agent_os.tools.vault import VaultTool
from agent_os.verifier import Verifier


class AgentOS:
    """Small stable core: observe -> plan -> act -> verify -> remember."""

    def __init__(self, workspace: str = ".", data_dir: str = "data", headless_browser: bool = False) -> None:
        self.workspace = Path(workspace).resolve()
        self.data_dir = Path(data_dir)
        self.memory = JsonlMemory(str(self.data_dir / "episodes.jsonl"))
feat/self-improvement-loop-17471436730359095752
        self.reflection_memory = ReflectionMemory(str(self.data_dir / "reflections.jsonl"))
        self.reflection_generator = ReflectionGenerator()
        self.proposer = ImprovementProposer()
        self.experiment_runner = ExperimentRunner(str(self.workspace))
        self.evaluator = EvolutionEvaluator()
        self.versioning = VersioningManager(str(self.workspace))

        self.logs_dir = Path("agent_os/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.skills_dir = self.data_dir / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        self.log_file = self.logs_dir / f"run_{now}.jsonl"
main
        self.vault = VaultTool(str(self.data_dir / "vault.json"))
        self.tools = ToolRegistry()
        self.tools.register(FileTool(str(self.workspace)))
        self.tools.register(ShellTool(str(self.workspace)))
        self.tools.register(self.vault)
        self.tools.register(HumanTool())
        self.tools.register(MonitorTool())
        self.tools.register(DeployTool())
        self.tools.register(EmailTool(self.vault))
        self.tools.register(BrowserTool(headless=headless_browser))
        self.planner = Planner(DEFAULT_SKILLS)
        self.verifier = Verifier()

    async def run_goal(self, description: str, **metadata) -> dict:
        goal = Goal(description=description, metadata=metadata)
        observation = self.observe(goal)

        saved_skill = self.find_similar_skill(description)
        if saved_skill:
            skill_name = "reused_skill"
            from agent_os.schemas import ActionRequest
            actions = [ActionRequest(**a) if isinstance(a, dict) else a for a in saved_skill.get("steps", [])]
        else:
            skill_name, actions = self.planner.plan(goal, observation)

        state = AgentState(goal=description, plan=actions)
        results = []
        for i, action in enumerate(actions):
            state.current_step = i + 1
            state.last_action = action
            result = await self.tools.run(action)
            state.last_result = result
            results.append(result)

            log_entry = {
                "step": i + 1,
                "goal": description,
                "plan_step": action.reason,
                "action": f"{action.tool}.{action.operation}",
                "input": action.params,
                "result": result.output if result.success else result.error,
                "success": result.success,
                "next_decision": "stop" if (result.requires_human or not result.success) else "continue"
            }
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, default=str) + "\n")

            if result.requires_human:
                break
            if not result.success:
                break
        state.blocked = any(not r.success for r in results) or any(r.requires_human for r in results)
        verification = self.verifier.verify(goal, state, results)
        goal.status = "completed" if verification.success else "blocked"

        if verification.success and not saved_skill:
            self.save_skill({
                "goal": description,
                "steps": [a.__dict__ if hasattr(a, '__dict__') else a for a in actions],
                "tools_used": list(set(a.tool for a in actions))
            })

        episode = Episode(goal, observation, actions, results, verification)
        record = episode.to_dict()
        record["skill"] = skill_name
        self.memory.append(record)

        reflection = self.reflection_generator.generate(episode)
        reflection["episode_id"] = record["goal"].get("goal_id", "")
        self.reflection_memory.append(reflection)

        proposal = self.proposer.propose(reflection)
        if proposal and proposal.get("type") == "skill":
            target_skill = proposal.get("target")
            # For this simple prototype, try to find a file matching the target
            target_file_path = f"agent_os/skills/{target_skill}.py"
            # Fallback to base.py if we don't have a matching skill for simulation
            if not (self.workspace / target_file_path).exists():
                 target_file_path = "agent_os/skills/base.py"

            test_results = self.experiment_runner.run_experiment(proposal, target_file_path)

            # Simulated old metrics
            old_metrics = {"success_rate": 0.5, "steps_taken": len(episode.actions)}

            if self.evaluator.evaluate(old_metrics, test_results):
                 modified_file = test_results.get("modified_file")
                 if modified_file:
                     self.versioning.promote(modified_file, Path(target_file_path).name)

        return record

    def observe(self, goal: Goal) -> Observation:
        related = self.memory.search(goal.description, limit=3)
        return Observation(
            summary=f"Goal received. Found {len(related)} related memory records.",
            data={"related_memory": related, "tools": self.tools.names()},
        )


    def find_similar_skill(self, goal_desc: str) -> dict | None:
        if not self.skills_dir.exists():
            return None
        needle = set(goal_desc.lower().split())
        best_skill = None
        best_score = 0.0
        for skill_file in self.skills_dir.glob("*.json"):
            try:
                skill_data = json.loads(skill_file.read_text(encoding="utf-8"))
                saved_goal = set(skill_data.get("goal", "").lower().split())
                if not saved_goal:
                    continue
                score = len(needle.intersection(saved_goal)) / len(saved_goal)
                if score > 0.7 and score > best_score:
                    best_score = score
                    best_skill = skill_data
            except Exception:
                continue
        return best_skill

    def save_skill(self, skill_data: dict) -> None:
        import uuid
        skill_id = str(uuid.uuid4())[:8]
        file_path = self.skills_dir / f"skill_{skill_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(skill_data, f, indent=2)
