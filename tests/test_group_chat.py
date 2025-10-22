# tests/test_group_chat.py
"""
Test AutoGen GroupChat functionality
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import logging
from app.agents.coding_agent import CodingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.behavior_agent import BehaviorAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.group_chat_manager import InterviewGroupChat, RoundRobinInterviewManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_roundrobin_groupchat():
    """Test RoundRobin GroupChat"""
    print("\n" + "=" * 70)
    print("🧪 TEST: RoundRobin GroupChat")
    print("=" * 70)
    
    # Create agents
    coding_agent = CodingAgent()
    resume_agent = ResumeAgent()
    behavior_agent = BehaviorAgent()
    evaluator_agent = EvaluatorAgent(mode="teach")
    
    # Create group chat
    group_chat = InterviewGroupChat(
        agents=[
            coding_agent.agent,
            resume_agent.agent,
            behavior_agent.agent,
            evaluator_agent.agent
        ],
        mode="roundrobin",
        max_turns=8
    )
    
    # Run collaborative interview
    initial_task = """
    We are conducting a technical interview.
    
    CodingAgent: Start by asking one coding question about data structures.
    ResumeAgent: Then ask about the candidate's Python experience.
    BehaviorAgent: Ask about teamwork.
    EvaluatorAgent: Provide guidance on what makes good answers.
    
    Keep responses concise (2-3 sentences each).
    """
    
    try:
        result = await group_chat.run_collaborative_interview(
            initial_task=initial_task,
            context={
                "resume": "Python developer with 3 years experience",
                "jd": "Looking for senior backend engineer",
                "mode": "teach"
            }
        )
        
        print("\n✅ Collaborative interview completed")
        print("\n📝 Conversation Summary:")
        print(group_chat.get_conversation_summary())
        
        print("\n❓ Extracted Questions:")
        questions = group_chat.extract_questions()
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        
        print("\n" + "=" * 70)
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        return False


async def test_roundrobin_manager():
    """Test RoundRobin Interview Manager"""
    print("\n" + "=" * 70)
    print("🧪 TEST: RoundRobin Interview Manager")
    print("=" * 70)
    
    # Create agents
    coding_agent = CodingAgent()
    resume_agent = ResumeAgent()
    behavior_agent = BehaviorAgent()
    evaluator_agent = EvaluatorAgent(mode="teach")
    
    # Create manager
    manager = RoundRobinInterviewManager(
        coding_agent=coding_agent.agent,
        resume_agent=resume_agent.agent,
        behavior_agent=behavior_agent.agent,
        evaluator_agent=evaluator_agent.agent,
        max_rounds=3
    )
    
    context = {
        "resume": "Python developer with 3 years experience at startups",
        "jd": "Looking for senior backend engineer with Python and system design skills"
    }
    
    try:
        # Conduct rounds
        while not manager.is_complete():
            round_type = manager.next_round()
            if round_type:
                print(f"\n🎯 Conducting {round_type.upper()} round...")
                result = await manager.conduct_round(round_type, context)
                print(f"✅ Question generated: {result['question'][:100]}...")
        
        print("\n✅ All rounds complete")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        return False


async def main():
    """Run all GroupChat tests"""
    print("\n" + "=" * 70)
    print("🚀 STARTING GROUPCHAT TESTS")
    print("=" * 70)
    
    # Test 1: RoundRobin GroupChat
    test1 = await test_roundrobin_groupchat()
    
    # Test 2: RoundRobin Manager
    test2 = await test_roundrobin_manager()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    print(f"RoundRobin GroupChat: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"RoundRobin Manager: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())