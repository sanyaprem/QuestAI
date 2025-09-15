# app/agents/resume_agent.py
from app.agents.base_agent import BaseAgent

class ResumeAgent(BaseAgent):
    def __init__(self):
        system = (
            "You are ResumeAgent: an interviewer focusing on the candidate's resume and the job description. "
            "Generate targeted questions about past projects, tools, technologies, and experience depth. "
            "Be specific and ask for details that reveal competence."
        )
        super().__init__(name="ResumeAgent", system_message=system)

    async def generate_questions(self, resume_text: str, jd_text: str, count: int = 3) -> str:
        prompt = (
            f"Based on the resume and job description below, produce {count} focused interview questions "
            "that probe the candidate's experience and skills. Number them.\n\n"
            f"Resume:\n{resume_text}\n\nJD:\n{jd_text}"
        )
        return await self.ask(prompt)
