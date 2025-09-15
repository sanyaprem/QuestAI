# app/agents/evaluator_agent.py
from app.agents.base_agent import BaseAgent
import json
import re

class EvaluatorAgent(BaseAgent):
    def __init__(self, mode: str = "experience"):
        """
        mode: 'experience' (brief feedback) or 'teach' (detailed guidance)
        """
        system = (
            "You are EvaluatorAgent: you score candidate answers and provide concise feedback. "
            "In 'teach' mode give actionable step-by-step improvement tips; in 'experience' mode give brief feedback."
        )
        super().__init__(name="EvaluatorAgent", system_message=system)
        self.mode = mode

    async def evaluate(self, question: str, answer: str) -> dict:
        """
        Ask the agent to evaluate the answer and return a dict:
        {'score': int, 'feedback': str, 'recommendations': [str,...]}
        """
        rubric = (
            f"You are scoring an interview response. Mode: {self.mode}\n\n"
            f"Question:\n{question}\n\nCandidate answer:\n{answer}\n\n"
            "Task:\n- Give a numeric score 0-10.\n- Provide a 2-3 sentence feedback summary.\n- Provide up to 3 short recommendations to improve.\nReturn ONLY a JSON object with keys: score, feedback, recommendations."
        )
        raw = await self.ask(rubric)

        # try to extract JSON payload
        try:
            m = re.search(r"\{.*\}", raw, re.S)
            json_text = m.group(0) if m else raw
            parsed = json.loads(json_text)
            # normalize keys
            return {
                "score": parsed.get("score"),
                "feedback": parsed.get("feedback") or parsed.get("explanation") or str(parsed),
                "recommendations": parsed.get("recommendations", [])
            }
        except Exception:
            # fallback: return raw text as feedback
            return {"score": None, "feedback": raw, "recommendations": []}

    def set_mode(self, mode: str):
        """Change mode at runtime (teach / experience)."""
        self.mode = mode
