from __future__ import annotations

import argparse
import asyncio
import json

from agent_os.loop import AgentOS


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Mini Daburu OS")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a goal")
    run.add_argument("goal")
    run.add_argument("--workspace", default=".")
    run.add_argument("--data-dir", default="data")
    run.add_argument("--headless-browser", action="store_true")

    tools = sub.add_parser("tools", help="List tools")
    tools.add_argument("--workspace", default=".")
    tools.add_argument("--data-dir", default="data")

    memory = sub.add_parser("memory", help="Show recent memory")
    memory.add_argument("--workspace", default=".")
    memory.add_argument("--data-dir", default="data")
    memory.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()
    osys = AgentOS(args.workspace, args.data_dir, headless_browser=getattr(args, "headless_browser", False))

    if args.command == "run":
        output = await osys.run_goal(args.goal)
    elif args.command == "tools":
        output = osys.tools.describe()
    elif args.command == "memory":
        output = osys.memory.recent(args.limit)
    else:
        raise RuntimeError(f"Unknown command: {args.command}")

    print(json.dumps(output, indent=2, default=str))


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
