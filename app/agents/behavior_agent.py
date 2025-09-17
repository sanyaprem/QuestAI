# app/agents/behavior_agent.py
from app.agents.base_agent import BaseAgent

class BehaviorAgent(BaseAgent):
    def __init__(self):
        system = (
            "You are BehaviorAgent: you ask behavioral interview questions (communication, teamwork, leadership, conflict resolution). "
            "Questions should be open-ended and invite the candidate to describe situations, actions, and results (STAR style). Ask questions to see if the candidate fits the company culture. Keep it conversational"
        )
        super().__init__(name="BehaviorAgent", system_message=system)

    async def generate_questions(self, count: int = 5) -> str:
        prompt = f"Generate {count} behavioral interview questions suitable for the job role in the job description."
        text = await self.ask(prompt)
        return [q.strip(" -0123456789.") for q in text.split("\n") if q.strip()]
        # return await self.ask(prompt)
