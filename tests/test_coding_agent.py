# tests/test_coding_agent.py
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from app.agents.coding_agent import CodingAgent

async def test_coding_agent_creation():
    print("\n🧪 TEST: Coding Agent Creation")
    print("=" * 60)
    agent = CodingAgent()
    print(f"✅ CodingAgent created: {agent.name}")
    print("=" * 60)
    return agent

async def test_generate_problem():
    print("\n🧪 TEST: Generate Coding Problem")
    print("=" * 60)
    agent = CodingAgent()
    problem = await agent.generate_problem(
        resume_text="Python developer with 3 years experience",
        jd_text="Looking for backend engineer",
        difficulty="medium"
    )
    print(f"✅ Problem generated:")
    print(f"{problem[:300]}...")
    print("=" * 60)

async def main():
    await test_coding_agent_creation()
    await test_generate_problem()
    print("\n✅ ALL CODING AGENT TESTS COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())