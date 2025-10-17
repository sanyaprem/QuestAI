# tests/test_base_agent.py
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from app.agents.base_agent import BaseAgent

async def test_agent_creation():
    print("\n🧪 TEST 1: Agent Creation")
    print("=" * 60)
    agent = BaseAgent(
        name="TestAgent",
        system_message="You are a test agent."
    )
    print(f"✅ Agent created: {agent.name}")
    print(f"✅ Call count: {agent.call_count}")
    print("=" * 60)
    return agent

async def test_agent_ask():
    print("\n🧪 TEST 2: Agent Ask")
    print("=" * 60)
    agent = BaseAgent(
        name="TestAgent",
        system_message="You are a helpful assistant."
    )
    try:
        response = await agent.ask("Say hello in one sentence")
        print(f"✅ Agent responded: {response[:100]}...")
        print(f"✅ Call count: {agent.call_count}")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        print("=" * 60)
        return False

async def test_agent_stats():
    print("\n🧪 TEST 3: Agent Stats")
    print("=" * 60)
    agent = BaseAgent("TestAgent", "You are a test agent")
    await agent.ask("Test 1")
    await agent.ask("Test 2")
    stats = agent.get_stats()
    print(f"✅ Stats: {stats}")
    print("=" * 60)

async def main():
    await test_agent_creation()
    await test_agent_ask()
    await test_agent_stats()
    print("\n✅ ALL AGENT TESTS COMPLETE")
    print("📁 Check logs/quest_ai.log for detailed logs")

if __name__ == "__main__":
    asyncio.run(main())