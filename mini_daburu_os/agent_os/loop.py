from __future__ import annotations

from pathlib import Path

from agent_os.memory.jsonl_memory import JsonlMemory, ReflectionMemory
from agent_os.learning.reflection import ReflectionGenerator
from agent_os.improvement.proposer import ImprovementProposer
from agent_os.experiment.sandbox import ExperimentRunner
from agent_os.evolution.evaluator import EvolutionEvaluator
from agent_os.evolution.versioning import VersioningManager
from agent_os.planner import Planner
from agent_os.schemas import Episode, Goal, Observation
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
        self.reflection_memory = ReflectionMemory(str(self.data_dir / "reflections.jsonl"))
        self.reflection_generator = ReflectionGenerator()
        self.proposer = ImprovementProposer()
        self.experiment_runner = ExperimentRunner(str(self.workspace))
        self.evaluator = EvolutionEvaluator()
        self.versioning = VersioningManager(str(self.workspace))
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
        skill_name, actions = self.planner.plan(goal, observation)
        results = []
        for action in actions:
            result = await self.tools.run(action)
            results.append(result)
            if result.requires_human:
                break
            if not result.success:
                break
        verification = self.verifier.verify(goal, results)
        goal.status = "completed" if verification.success else "blocked"
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
