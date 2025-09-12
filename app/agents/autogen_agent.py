from autogen_agentchat.agents import AssistantAgent, UserMessage

class AutogenAgent:
    def __init__(self, name="Assistant"):
        self.agent = AssistantAgent(name=name)

    def ask(self, question: str) -> str:
        # Wrap the question into a UserMessage
        user_msg = UserMessage(text=question)
        # Get response from the agent
        response = self.agent.chat([user_msg])
        return response[0].text  # Extract the text from the response
