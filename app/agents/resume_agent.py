# app/agents/resume_agent.py
import logging
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResumeAgent(BaseAgent):
    """Agent responsible for resume-based questions"""
    
    def __init__(self):
        system = (
            "You are ResumeAgent: an interviewer focusing on the candidate's resume and the job description. "
            "Generate targeted questions about past projects, tools, technologies, and experience depth. "
            "Be specific and ask for details that reveal competence. Keep it conversational."
        )
        super().__init__(name="ResumeAgent", system_message=system)
        logger.info("ResumeAgent initialized")

    async def generate_questions(self, resume_text: str, jd_text: str) -> list:
        """Generate resume-based questions"""
        logger.info("Generating resume-based questions")
        logger.debug(f"Resume: {len(resume_text)} chars, JD: {len(jd_text)} chars")
        
        prompt = (
            f"Based on the resume and job description below, produce 3-4 focused interview questions "
            "that probe the candidate's experience and skills. Number them.\n\n"
            f"Resume:\n{resume_text[:1000]}\n\nJD:\n{jd_text[:1000]}"
        )
        
        text = await self.ask(prompt)
        
        # Parse into list of questions
        questions = [q.strip(" -0123456789.") for q in text.split("\n") if q.strip()]
        
        logger.info(f"Generated {len(questions)} resume questions")
        return questions


logger.info("ResumeAgent module loaded")