from fastapi import FastAPI
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()

model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",
    api_key='AIzaSyCGxXSZUjMbjuFqmdWkHUWWX1KehwTlKxk'
)


app = FastAPI()
agent = AssistantAgent(
    name="QuestAI",
    system_message="You are QuestAI, an interview assistant helping users practice technical interviews.",
    model_client=model_client
)



class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(query: Query):
    response = await agent.run(task=query.question)
    return {"answer": response.messages[-1].content}

