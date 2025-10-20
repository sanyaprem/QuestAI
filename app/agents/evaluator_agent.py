# app/agents/evaluator_agent.py
import logging
from app.agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import re

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """Agent responsible for evaluating candidate responses"""
    
    def __init__(self, mode: str = "experience"):
        """
        Initialize evaluator agent
        
        Args:
            mode: 'experience' (brief feedback) or 'teach' (detailed guidance)
        """
        system = (
            "You are EvaluatorAgent: given a question and a candidate's answer, "
            "provide a numeric score 0–10, a short feedback paragraph, "
            "and up to 3 concrete recommendations. "
            "Return ONLY valid JSON: {\"score\": int, \"feedback\": str, \"recommendations\": [str]}. "
            "If the answer is empty or irrelevant, give a low score and note that in feedback"
        )
        super().__init__(name="EvaluatorAgent", system_message=system)
        self.mode = mode
        logger.info(f"EvaluatorAgent initialized with mode: {mode}")

    async def evaluate(self, question: str, answer: str, round_type: str = "coding", retry: bool = False) -> Dict[str, Any]:
        """
        Evaluate a candidate's answer
        
        Args:
            question: The interview question
            answer: Candidate's answer
            round_type: Type of round (coding, resume, behavior)
            retry: Whether this is a retry attempt
            
        Returns:
            Dictionary with score, feedback, and recommendations
        """
        logger.info(f"Evaluating {round_type} answer")
        logger.debug(f"Question: {question[:100]}...")
        logger.debug(f"Answer: {answer[:100]}...")
        
        prompt = (
            f"QUESTION:\n{question}\n\nCANDIDATE ANSWER:\n{answer}\n\n"
            f"Evaluate this answer for a {round_type} interview round. "
            "Return JSON: {\"score\": int, \"feedback\": str, \"recommendations\": [str]}."
        )
        
        raw = await self.ask(prompt)
        logger.debug(f"Raw evaluation response: {raw[:200]}...")
        
        try:
            # Try to extract JSON from response
            m = re.search(r"\{.*\}", raw, re.S)
            parsed = json.loads(m.group(0)) if m else json.loads(raw)
            
            result = {
                "score": int(parsed.get("score", 0)),
                "feedback": parsed.get("feedback", "").strip(),
                "recommendations": parsed.get("recommendations", []),
            }
            
            logger.info(f"✅ Evaluation complete - Score: {result['score']}/10")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to parse evaluation: {str(e)}")
            logger.debug(f"Raw response was: {raw}")
            
            return {
                "score": 0,
                "feedback": f"Could not parse evaluation. Raw: {raw[:300]}",
                "recommendations": ["Retry evaluation"],
            }

    def set_mode(self, mode: str):
        """Change mode at runtime (teach / experience)"""
        logger.info(f"Changing evaluator mode from {self.mode} to {mode}")
        self.mode = mode


logger.info("EvaluatorAgent module loaded")