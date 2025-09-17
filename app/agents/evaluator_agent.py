# app/agents/evaluator_agent.py
from app.agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import re

class EvaluatorAgent(BaseAgent):
    def __init__(self, mode: str = "experience"):
        """
        mode: 'experience' (brief feedback) or 'teach' (detailed guidance)
        """
        system = (
            "You are EvaluatorAgent: given a question and a candidate's answer, "
            "provide a numeric score 0–10, a short feedback paragraph, "
            "and up to 3 concrete recommendations. "
            "Return ONLY valid JSON: {\"score\": int, \"feedback\": str, \"recommendations\": [str]}."
            "If the answert is empty or irrelevant, give a low score and note that in feedback"
        )
        super().__init__(name="EvaluatorAgent", system_message=system)
        self.mode = mode

    async def evaluate(self, question: str, answer: str, round_type: str = "coding", retry: bool = False) -> Dict[str, Any]:
        prompt = (
            f"QUESTION:\n{question}\n\nCANDIDATE ANSWER:\n{answer}\n\n"
            f"Evaluate this answer for a {round_type} interview round. "
            "Return JSON: {\"score\": int, \"feedback\": str, \"recommendations\": [str]}."
        )
        raw = await self.ask(prompt)
        try:
            m = re.search(r"\{.*\}", raw, re.S)
            parsed = json.loads(m.group(0)) if m else json.loads(raw)
            return {
                "score": int(parsed.get("score", 0)),
                "feedback": parsed.get("feedback", "").strip(),
                "recommendations": parsed.get("recommendations", []),
            }
        except Exception:
            return {
                "score": 0,
                "feedback": f"Could not parse evaluation. Raw: {raw[:300]}",
                "recommendations": ["Retry evaluation"],
            }

    def set_mode(self, mode: str):
        """Change mode at runtime (teach / experience)."""
        self.mode = mode
