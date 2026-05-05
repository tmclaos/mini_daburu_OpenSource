import asyncio
from agent_os.loop import AgentOS

async def main():
    os = AgentOS(data_dir="data_test")
    await os.run_goal("deploy ./demo-app to vercel")

    with open("data_test/reflections.jsonl", "r") as f:
        print(f.read())

if __name__ == "__main__":
    asyncio.run(main())
