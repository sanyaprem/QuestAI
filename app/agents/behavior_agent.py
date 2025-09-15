# app/agents/behavior_agent.py
from app.agents.base_agent import BaseAgent

class BehaviorAgent(BaseAgent):
    def __init__(self):
        system = (
            "You are BehaviorAgent: you ask behavioral interview questions (communication, teamwork, leadership, conflict resolution). "
            "Questions should be open-ended and invite the candidate to describe situations, actions, and results (STAR style)."
        )
        super().__init__(name="BehaviorAgent", system_message=system)

    async def generate_questions(self, count: int = 5) -> str:
        prompt = f"Generate {count} behavioral interview questions suitable for a software engineering role. Number them."
        return await self.ask(prompt)
