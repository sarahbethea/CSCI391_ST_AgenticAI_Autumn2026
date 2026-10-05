import os
import sys
import requests
import json
from dotenv import load_dotenv
from tavily import TavilyClient

MAX_STEPS = 7

def calculator(expression):
    # TODO 1: Implement a simple calculator tool.
    # Return a string containing the calculation result.
    try:
        allowed_characters = "0123456789+-*/().% "

        if not all(char in allowed_characters for char in expression):
            return "Error: expression contains invalid characters."

        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)

    except Exception as error:
        return f"Calculator error: {error}"

def search_web(query):
    # TODO 2: Reuse your Lab 1 web-search implementation.
    # Return a concise string containing useful search results.
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key=tavily_api_key)
    search_results = client.search(query, search_depth="advanced")
    return str(search_results["results"][:3])

def main(args):
    load_dotenv()

    # TODO 3: Read the OpenRouter API key from the environment.
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    # TODO 4: Set the model. You may reuse the model you selected in Lab 1.
    model = args[0] if args else "openrouter/free"
    #"nvidia/nemotron-3-super-120b-a12b:free"

    SYSTEM_PROMPT = """
    You are a helpful research agent.

    Your goal is to answer the user's question accurately.
    You may use the available tools when additional information
    or calculation is necessary.

    After observing a tool result, decide what to do next.
    Stop when you have enough information to provide a final answer.
    """

    # TODO 5: Define your tool descriptions.
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": (
                    "Evaluate a mathematical expression. "
                    "Use this tool when arithmetic is needed."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": (
                                "The mathematical expression to evaluate, "
                                "such as '(12 * 5) + 3'."
                            )
                        }
                    },
                    "required": ["expression"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for information needed to answer the user's question. Provide a concise search query describing the specific information you need.",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "Web search query."
                    }
                },
                "required": ["query"]
            }
        }
    ]

    messages = []

    user_input = input("What would you like me to investigate?\n")
    messages.append({"role": "user", "content": user_input})

    for step in range(1, MAX_STEPS + 1):

        print(f"\n--- STEP {step} ---")

        # TODO 6: Send the current conversation to the model.
        # Include the system prompt and tool definitions.
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": (f"Bearer {openrouter_api_key}"),
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                *messages
            ],
            "tools": tools
        }
        response = requests.post(url, headers=headers, json=payload)

        if not response.ok:
            print(response.status_code, response.text)
            return

        # TODO 7: Extract the model's message and any requested tool calls.
        response_data = response.json()
        if "choices" not in response_data:
            print("OpenRouter returned an error:")
            print(response_data)
            return

        message = response_data["choices"][0]["message"]
        tool_calls = message.get("tool_calls", [])

        # TODO 8: If the model did not request a tool,
        # print its response and terminate the loop.
        if not tool_calls:
            print(message["content"])
            return

        # TODO 9: Append the model's message to the conversation.
        messages.append(message)

        for call in tool_calls:
            # TODO 10: Determine which tool was requested and execute it.
            tool_name = call["function"]["name"]
            arguments = json.loads(call["function"]["arguments"])

            if tool_name == "calculator":
                tool_result = calculator(arguments["expression"])
            elif tool_name == "search_web":
                tool_result = search_web(arguments["query"])

            # TODO 11: Print the action and observation.
            print("ACTION:", tool_name, arguments)
            print("OBSERVATION:", tool_result)

            # TODO 12: Append the tool result to messages.
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": str(tool_result)
            })

    else:
        print("\nAgent stopped: maximum step budget reached.")

if __name__ == "__main__":
    main(sys.argv[1:])