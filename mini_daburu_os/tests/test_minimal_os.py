import asyncio
import shutil
import unittest
from pathlib import Path

from agent_os.loop import AgentOS
from agent_os.memory import JsonlMemory
from agent_os.schemas import ActionResult, Goal, AgentState
from agent_os.verifier import Verifier


TEST_ROOT = Path(__file__).resolve().parents[1] / ".test_tmp"


class LocalTemp:
    def __enter__(self):
        if TEST_ROOT.exists():
            shutil.rmtree(TEST_ROOT)
        TEST_ROOT.mkdir(parents=True)
        return TEST_ROOT

    def __exit__(self, exc_type, exc, tb):
        if TEST_ROOT.exists():
            shutil.rmtree(TEST_ROOT)


class MiniDaburuTests(unittest.TestCase):
    def test_memory_round_trip(self):
        with LocalTemp() as td:
            memory = JsonlMemory(str(td / "episodes.jsonl"))
            memory.append({"goal": "hello", "success": True})
            self.assertEqual(memory.recent(1)[0]["goal"], "hello")
            self.assertEqual(memory.search("hello")[0]["success"], True)

    def test_verifier_success_and_checkpoint(self):
        verifier = Verifier()
        goal = Goal("test")
        state1 = AgentState(goal="test")
        ok = verifier.verify(goal, state1, [ActionResult(True)])
        state2 = AgentState(goal="test")
        blocked = verifier.verify(goal, state2, [ActionResult(False, requires_human=True, checkpoint="captcha")])
        self.assertTrue(ok.success)
        self.assertFalse(blocked.success)
        self.assertEqual(blocked.evidence["checkpoints"], ["captcha"])

    def test_agent_deploy_plan_goal(self):
        async def run():
            with LocalTemp() as td:
                workspace = td / "workspace"
                workspace.mkdir()
                data = td / "data"
                osys = AgentOS(str(workspace), str(data), headless_browser=True)
                result = await osys.run_goal("deploy . to vercel")
                self.assertEqual(result["skill"], "deploy_app")
                self.assertTrue(result["results"][0]["success"])
                self.assertTrue((data / "episodes.jsonl").exists())

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
