from app.agents.base_agent import BaseAgent

class CodingAgent(BaseAgent):
    def __init__(self):
        system = (
            "You are CodingAgent: an interviewer that ONLY asks and clarifies coding problems based on Data structures and algorithms. "
            "When asked to generate a problem, produce a clear statement, constraints, sample input/output, "
            "and indicate complexity expectations. Keep wording precise and unambiguous."
        )
        super().__init__(name="CodingAgent", system_message=system)

    async def generate_problem(self, resume_text: str = "", jd_text: str = "", difficulty: str = "medium") -> str:
        prompt = (
            f"Generate ONE {difficulty} difficulty coding interview problem relevant to this role.\n"
            f"Resume context:\n{resume_text}\n\nJob description:\n{jd_text}\n\n"
            "Return only the problem statement, constraints, and sample I/O."
        )
        return await self.ask(prompt)   # ✅ calls BaseAgent.ask

    async def generate_followups(self, problem_statement: str) -> str:
        prompt = (
            f"The following problem was asked:\n{problem_statement}\n\n"
            "Produce 2 short follow-up prompts that ask the candidate for:\n"
            "1) an outline of brute-force approach, 2) a better/optimal approach and time/space complexity.\n"
            "Return as bullet lines."
        )
        return await self.ask(prompt)   # ✅ calls BaseAgent.ask
