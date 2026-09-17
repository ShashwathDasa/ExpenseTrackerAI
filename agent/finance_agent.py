import json
from datetime import date
import agent.tools
from groq import Groq

from agent.system_prompt import get_system_prompt
from config import Config
from agent.tool_registry import get_tool_definitions, call_tool


class FinanceAgent:

    def __init__(self, session):
        self.session = session
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = "openai/gpt-oss-120b"

    def respond(self, user_message, history=None):
        today = date.today().isoformat()
        system_prompt = get_system_prompt(today)
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})

        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=get_tool_definitions(),
                tool_choice="auto",
            )

            message = response.choices[0].message
            if not message.tool_calls:
                messages.append({"role": "assistant", "content": message.content})
                return message.content, messages[1:]

            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ],
            })
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                result = call_tool(tool_name, self.session, arguments)

                messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_name,
                                 "content": json.dumps(result)})