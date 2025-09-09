from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

app = FastAPI()

class Query(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "AI Agent is running"}

@app.post("/ask")
def ask_question(query: Query):
    return {"response": f"You asked: {query.question}"}
