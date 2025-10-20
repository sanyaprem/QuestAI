# app/agents/behavior_agent.py
import logging
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BehaviorAgent(BaseAgent):
    """Agent responsible for behavioral interview questions"""
    
    def __init__(self):
        system = (
            "You are BehaviorAgent: you ask behavioral interview questions (communication, teamwork, leadership, conflict resolution). "
            "Questions should be open-ended and invite the candidate to describe situations, actions, and results (STAR style). "
            "Ask questions to see if the candidate fits the company culture. Keep it conversational"
        )
        super().__init__(name="BehaviorAgent", system_message=system)
        logger.info("BehaviorAgent initialized")

    async def generate_questions(self, count: int = 5) -> list:
        """Generate behavioral interview questions"""
        logger.info(f"Generating {count} behavioral questions")
        
        prompt = f"Generate {count} behavioral interview questions suitable for the job role in the job description."
        
        text = await self.ask(prompt)
        
        # Parse into list of questions
        questions = [q.strip(" -0123456789.") for q in text.split("\n") if q.strip()]
        
        logger.info(f"Generated {len(questions)} behavioral questions")
        return questions


logger.info("BehaviorAgent module loaded")