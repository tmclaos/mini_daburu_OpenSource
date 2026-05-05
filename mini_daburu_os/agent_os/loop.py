from __future__ import annotations

from pathlib import Path

from agent_os.memory import JsonlMemory
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
        return record

    def observe(self, goal: Goal) -> Observation:
        related = self.memory.search(goal.description, limit=3)
        return Observation(
            summary=f"Goal received. Found {len(related)} related memory records.",
            data={"related_memory": related, "tools": self.tools.names()},
        )
