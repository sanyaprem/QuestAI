import gradio as gr
import requests

def ask_agent(question):
    response = requests.post("http://127.0.0.1:8000/ask", json={"question": question})
    return response.json().get("response")

iface = gr.Interface(fn=ask_agent, inputs="text", outputs="text", title="QuestAI")
iface.launch()
