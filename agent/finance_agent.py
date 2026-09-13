import json

from groq import Groq

from config import Config
from agent.tool_registry import get_tool_definitions, call_tool


class FinanceAgent:

    def __init__(self, session):
        self.session = session
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = "openai/gpt-oss-120b"

    def respond(self, user_message):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a personal finance assistant. "
                    "Use the available tools to answer questions about "
                    "the user's financial data. "
                    "All financial amounts are in Indian Rupees (INR). "
                    "Always display monetary amounts using the ₹ symbol. "
                    "Do not convert amounts to another currency. "
                    "Do not invent financial figures."
                ),
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=get_tool_definitions(),
            tool_choice="auto",
        )

        message = response.choices[0].message
        if not message.tool_calls:
            return message.content
        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = call_tool(tool_name, self.session, arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(result),
                }
            )
        final_response = self.client.chat.completions.create(model=self.model, messages=messages)
        return final_response.choices[0].message.content