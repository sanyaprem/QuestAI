# app/agents/base_agent.py
import asyncio
import json
from typing import Any
from app.config import model_client   # ✅ import shared client

try:
    from autogen_agentchat.agents import AssistantAgent
except Exception:
    try:
        from autogen import AssistantAgent
    except Exception as e:
        raise ImportError("Could not import AssistantAgent.") from e


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value


class BaseAgent:
    def __init__(self, name: str, system_message: str):
        self.agent = AssistantAgent(
            name=name,
            system_message=system_message,
            model_client=model_client   # ✅ now defined
        )

    # app/agents/base_agent.py

    async def ask(self, prompt: str) -> str:
        try:
            # Call the model with a single user message
            result = await self.agent.run(task=prompt)
    
            # Extract only the last assistant message
            if hasattr(result, "messages") and result.messages:
                return result.messages[-1].content
    
            # If it's already a plain object
            if hasattr(result, "content"):
                return result.content
    
            return str(result)
    
        except Exception as e:
            return f"ERROR_CALLING_AGENT: {e}"


    
