# from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()

# # --- Gemini Config ---
# GEMINI_API_KEY = os.getenv("gemini_api_key")
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-8b")
# GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

# # --- OpenRouter Config ---
# OPENROUTER_API_KEY = os.getenv("openrouter_api_key")
# OPENROUTER_MODEL = os.getenv("openrouter_model", "deepseek/deepseek-chat-v3.1:free")
# OPENROUTER_BASE_URL = os.getenv("openrouter_base_url", "https://openrouter.ai/api/v1")

# # --- General Defaults ---
# DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini")  # "gemini" | "openrouter"
# model_client = OpenAIChatCompletionClient(
#      base_url="https://openrouter.ai/api/v1",
#      model="deepseek/deepseek-chat-v3.1:free",
#      api_key = os.getenv("OPENROUTER_API_KEY"),
#      model_info={
#          "family":'deepseek',
#          "vision" :True,
#          "function_calling":True,
#          "json_output": False
#      }
# )

model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",
    api_key=os.getenv("GEMINI_API_KEY")
)