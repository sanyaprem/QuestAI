from app.agents.base_agent import BaseAgent

class CodingAgent(BaseAgent):
    def __init__(self):
        system = (
            "You are CodingAgent: an interviewer that asks and clarifies coding problems based on Data structures and algorithms. If the candidate has experience of 3 or more years, then ask system design questions as well, else stick to data structures and algorithms. "
            "When asked to generate a problem, produce a clear statement, constraints, sample input/output, "
            "and indicate complexity expectations. Keep wording precise and unambiguous. After the candidate answers, ask follow up questions to test the candidate's understanding of different approaches and trade-offs."
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
    
    async def followups_for_answer(self, problem_statement: str, candidate_answer: str) -> str:
        prompt = (
            f"Problem:\n{problem_statement}\n\n"
            f"Candidate's answer:\n{candidate_answer}\n\n"
            "Ask 2–3 follow-up questions probing reasoning, edge cases, or complexity. "
            "Keep them short and conversational."
        )
        return await self.ask(prompt)