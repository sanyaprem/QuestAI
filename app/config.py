# from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()

model_client = OpenAIChatCompletionClient(
    base_url="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat-v3.1:free",
    api_key = os.getenv("api_key"),
    model_info={
        "family":'deepseek',
        "vision" :True,
        "function_calling":True,
        "json_output": False
    }

)