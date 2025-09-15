# from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()

model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",
    api_key= os.getenv("api_key")

)