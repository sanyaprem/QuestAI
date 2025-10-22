# app/agents/group_chat_manager.py
"""
GroupChat Manager for AutoGen Multi-Agent Collaboration
Implements RoundRobin and Selective Speaker patterns
"""
import logging
from typing import List, Dict, Optional, Any
from app.config import ModelClientFactory, Config

# Import AutoGen team components
try:
    from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.base import TaskResult
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import AutoGen team components: {e}")
    raise

logger = logging.getLogger(__name__)


class InterviewGroupChat:
    """
    Manages multi-agent collaboration for interview scenarios.
    Supports both RoundRobin (sequential) and Selector (dynamic) modes.
    """
    
    def __init__(
        self,
        agents: List[AssistantAgent],
        mode: str = "roundrobin",
        max_turns: int = 10
    ):
        """
        Initialize the group chat manager.
        
        Args:
            agents: List of AutoGen agents to participate
            mode: "roundrobin" for sequential, "selector" for dynamic
            max_turns: Maximum conversation turns
        """
        logger.info("=" * 70)
        logger.info("🎭 Creating InterviewGroupChat")
        logger.info(f"Mode: {mode} | Max turns: {max_turns}")
        logger.info("=" * 70)
        
        self.agents = agents
        self.mode = mode
        self.max_turns = max_turns
        self.conversation_history: List[Dict] = []
        
        # Create appropriate team based on mode
        if mode == "roundrobin":
            self.team = RoundRobinGroupChat(
                participants=agents,
                max_turns=max_turns
            )
            logger.info("✅ RoundRobinGroupChat created")
        elif mode == "selector":
            # Selector mode requires a selector agent
            model_client = ModelClientFactory.get_client()
            
            selector_agent = AssistantAgent(
                name="InterviewCoordinator",
                system_message="""
                You are the Interview Coordinator. Your role is to:
                1. Decide which agent should speak next
                2. Ensure all aspects of the interview are covered
                3. Keep the conversation focused and productive
                
                Available agents:
                - CodingAgent: For technical/coding questions
                - ResumeAgent: For experience-based questions
                - BehaviorAgent: For soft skills/behavioral questions
                - EvaluatorAgent: For scoring and feedback
                
                Always select the most appropriate agent for the current context.
                """,
                model_client=model_client
            )
            
            self.team = SelectorGroupChat(
                participants=agents,
                model_client=model_client,
                selector_prompt="Select the next agent to speak based on interview flow.",
                max_turns=max_turns
            )
            logger.info("✅ SelectorGroupChat created")
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        logger.info(f"Participants: {[a.name for a in agents]}")
        logger.info("=" * 70)
    
    async def run_collaborative_interview(
        self,
        initial_task: str,
        context: Optional[Dict] = None
    ) -> TaskResult:
        """
        Run a collaborative interview session.
        
        Args:
            initial_task: Starting prompt for the interview
            context: Additional context (resume, JD, etc.)
            
        Returns:
            TaskResult with conversation history
        """
        logger.info("=" * 70)
        logger.info("🚀 Starting Collaborative Interview")
        logger.info("=" * 70)
        logger.info(f"Initial task: {initial_task[:100]}...")
        
        # Build context-aware task
        if context:
            task = f"""
            Interview Context:
            - Resume: {context.get('resume', '')[:200]}...
            - Job Description: {context.get('jd', '')[:200]}...
            - Mode: {context.get('mode', 'standard')}
            
            Task: {initial_task}
            """
        else:
            task = initial_task
        
        try:
            # Run the team collaboration
            logger.info("Running team collaboration...")
            result = await self.team.run(task=task)
            
            # Extract conversation
            if hasattr(result, 'messages'):
                self.conversation_history = [
                    {
                        "agent": msg.source if hasattr(msg, 'source') else "unknown",
                        "content": msg.content if hasattr(msg, 'content') else str(msg)
                    }
                    for msg in result.messages
                ]
            
            logger.info(f"✅ Collaboration complete - {len(self.conversation_history)} messages")
            logger.info("=" * 70)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error in collaborative interview: {e}", exc_info=True)
            raise
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation.
        
        Returns:
            Formatted conversation summary
        """
        summary = "=" * 60 + "\n"
        summary += "INTERVIEW CONVERSATION SUMMARY\n"
        summary += "=" * 60 + "\n\n"
        
        for i, msg in enumerate(self.conversation_history, 1):
            agent = msg.get('agent', 'Unknown')
            content = msg.get('content', '')
            summary += f"[{i}] {agent}:\n{content}\n\n"
        
        return summary
    
    def extract_questions(self) -> List[str]:
        """
        Extract questions from the conversation.
        
        Returns:
            List of questions asked during interview
        """
        questions = []
        
        for msg in self.conversation_history:
            content = msg.get('content', '')
            agent = msg.get('agent', '')
            
            # Look for question patterns
            if '?' in content and agent != 'EvaluatorAgent':
                # Split by newlines and find question lines
                lines = content.split('\n')
                for line in lines:
                    if '?' in line and len(line.strip()) > 10:
                        questions.append(line.strip())
        
        logger.info(f"Extracted {len(questions)} questions from conversation")
        return questions
    
    def reset(self):
        """Reset the group chat state"""
        logger.info("🔄 Resetting group chat")
        self.conversation_history = []


class RoundRobinInterviewManager:
    """
    Simplified RoundRobin manager for structured interviews.
    Each agent speaks in order until all rounds are complete.
    """
    
    def __init__(
        self,
        coding_agent: AssistantAgent,
        resume_agent: AssistantAgent,
        behavior_agent: AssistantAgent,
        evaluator_agent: AssistantAgent,
        max_rounds: int = 3
    ):
        """
        Initialize the RoundRobin interview manager.
        
        Args:
            coding_agent: Agent for coding questions
            resume_agent: Agent for resume-based questions
            behavior_agent: Agent for behavioral questions
            evaluator_agent: Agent for evaluation
            max_rounds: Maximum interview rounds
        """
        self.agents = {
            "coding": coding_agent,
            "resume": resume_agent,
            "behavior": behavior_agent,
            "evaluator": evaluator_agent
        }
        self.max_rounds = max_rounds
        self.current_round = 0
        self.round_sequence = ["coding", "resume", "behavior"]
        
        logger.info("✅ RoundRobinInterviewManager initialized")
        logger.info(f"Sequence: {' → '.join(self.round_sequence)}")
    
    async def conduct_round(
        self,
        round_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Conduct a single interview round.
        
        Args:
            round_type: Type of round (coding/resume/behavior)
            context: Interview context
            
        Returns:
            Round results
        """
        logger.info(f"🎯 Conducting {round_type} round")
        
        agent = self.agents[round_type]
        
        # Build prompt based on round type
        if round_type == "coding":
            prompt = f"""
            Generate a coding interview question.
            Resume: {context.get('resume', '')[:300]}
            JD: {context.get('jd', '')[:300]}
            """
        elif round_type == "resume":
            prompt = f"""
            Generate technical questions based on experience.
            Resume: {context.get('resume', '')[:500]}
            """
        elif round_type == "behavior":
            prompt = "Generate behavioral interview questions using STAR method."
        else:
            prompt = f"Generate {round_type} questions."
        
        # Get question from agent
        result = await agent.run(task=prompt)
        question = self._extract_response(result)
        
        logger.info(f"✅ {round_type.capitalize()} round complete")
        
        return {
            "round_type": round_type,
            "question": question,
            "agent": agent.name
        }
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate an answer using the evaluator agent.
        
        Args:
            question: The interview question
            answer: Candidate's answer
            
        Returns:
            Evaluation results
        """
        evaluator = self.agents["evaluator"]
        
        prompt = f"""
        Evaluate this interview response:
        
        QUESTION: {question}
        ANSWER: {answer}
        
        Provide JSON with: score (0-10), feedback, recommendations
        """
        
        result = await evaluator.run(task=prompt)
        evaluation = self._extract_response(result)
        
        return evaluation
    
    def _extract_response(self, result: Any) -> str:
        """Extract text from agent result"""
        if hasattr(result, "messages") and result.messages:
            return result.messages[-1].content
        if hasattr(result, "content"):
            return result.content
        return str(result)
    
    def next_round(self) -> Optional[str]:
        """
        Get the next round type.
        
        Returns:
            Next round type or None if complete
        """
        if self.current_round < len(self.round_sequence):
            round_type = self.round_sequence[self.current_round]
            self.current_round += 1
            return round_type
        return None
    
    def is_complete(self) -> bool:
        """Check if all rounds are complete"""
        return self.current_round >= len(self.round_sequence)


logger.info("✅ GroupChat Manager module loaded")