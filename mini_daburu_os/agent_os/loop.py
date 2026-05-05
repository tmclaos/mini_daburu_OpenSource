from __future__ import annotations

from pathlib import Path

from agent_os.memory import JsonlMemory, StructuredMemory
from agent_os.planner import PlanningEngine
from agent_os.schemas import Episode, Goal, Observation, State
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
from agent_os.tools.api import APITool
from agent_os.verifier import Verifier
from agent_os.logger import TraceLogger


class AgentOS:
    """Small stable core: observe -> plan -> act -> verify -> remember."""

    def __init__(self, workspace: str = ".", data_dir: str = "data", headless_browser: bool = False) -> None:
        self.workspace = Path(workspace).resolve()
        self.data_dir = Path(data_dir)
        self.memory = JsonlMemory(str(self.data_dir / "episodes.jsonl"))
        self.structured_memory = StructuredMemory(str(self.data_dir))
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
        self.tools.register(APITool())
        self.planner = PlanningEngine(DEFAULT_SKILLS)
        self.verifier = Verifier()
        self.logger = TraceLogger(str(self.data_dir / "trace.jsonl"))
        self.state = State()

    async def run_goal(self, description: str, **metadata) -> dict:
        goal = Goal(description=description, metadata=metadata)
        self.state.goal = goal
        self.logger.log_goal_started(goal)

        observation = self.observe(goal)
        self.logger.log_observation(observation)

        max_retries = 3
        retries = 0
        results = []
        actions = []
        skill_name = "unknown"

        while retries < max_retries:
            skill_name, current_actions = self.planner.plan(goal, observation)
            self.logger.log_plan(skill_name, current_actions)

            current_results = []
            error_detected = False

            for action in current_actions:
                self.logger.log_action_started(action)
                self.state.last_action = action

                result = await self.tools.run(action)
                self.logger.log_action_result(result)
                self.state.last_result = result

                current_results.append(result)
                actions.append(action)
                results.append(result)

                if result.requires_human:
                    error_detected = True
                    break

                if not result.success:
                    self.state.blockers.append(result.error)
                    observation.data["last_error"] = result.error
                    error_detected = True
                    break

            if not error_detected:
                break

            retries += 1
            if retries < max_retries:
                # Update observation to reflect the failure and trigger Strategy Switching
                observation.summary = f"Retry {retries}/{max_retries} due to error. Searching alternative strategies."

        verification = self.verifier.verify(goal, results)
        goal.status = "completed" if verification.success else "blocked"
        self.logger.log_goal_completed(goal, verification.success, verification.reason)

        episode = Episode(goal, observation, actions, results, verification)
        record = episode.to_dict()
        record["skill"] = skill_name

        # Self-Reflection (Phase 6)
        reflection = self.reflect(episode)
        if reflection:
            record["reflection"] = reflection.to_dict()

        self.memory.append(record)
        return record

    def reflect(self, episode: Episode):
        from agent_os.schemas import Experience

        if episode.verification.success:
            return Experience(
                lesson=f"Successfully completed: {episode.goal.description}. Actions taken: {len(episode.actions)}",
                context={"success": True, "goal": episode.goal.description}
            )
        else:
            return Experience(
                lesson=f"Failed to complete: {episode.goal.description}. Reason: {episode.verification.reason}",
                context={"success": False, "goal": episode.goal.description, "errors": self.state.blockers}
            )

    def observe(self, goal: Goal) -> Observation:
        related = self.memory.search(goal.description, limit=3)

        # Phase 3: Retrieve relevant past experiences
        experiences = []
        for r in related:
            if "reflection" in r:
                experiences.append(r["reflection"])

        # Phase 9: Instruction memory
        user_instructions = self.structured_memory.get_instructions("user_preferences")

        return Observation(
            summary=f"Goal received. Found {len(related)} related memory records and {len(experiences)} relevant experiences.",
            data={
                "related_memory": related,
                "experiences": experiences,
                "user_instructions": user_instructions,
                "tools": self.tools.names()
            },
        )
