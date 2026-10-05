import os
import sys
import requests
import json
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from tavily import TavilyClient


MAX_STEPS = 15
WINDOW_SIZE = 5
SYSTEM_PROMPT = """
    You are a helpful stock research agent.

    Your goal is to answer the user's question accurately.
    You may use the available tools when additional information
    or calculation is necessary.

    After observing a tool result, decide what to do next.
    Stop when you have enough information to provide a final answer.

    For stock comparisons, obtain a snapshot for each requested ticker. Use the calculator tool to compute each momentum_score using the specified formula. Once the comparison is complete, call final_answer. Do not finish with an ordinary text response. Do not invent missing snapshot data or calculator results. 
    """

PERSISTENT_CONSTRAINTS = """
    REMINDER — these constraints apply on every step, not just the first:
    1. Never state a ticker's price or day-change unless it came from a
    get_stock_snapshot() observation in this conversation.
    2. If a tool result is an error object, tell the user what failed —
    do not treat the error object as if it were valid data.
    3. final_answer's comparison_table must include all four requested
    tickers, each backed by an actual get_stock_snapshot() observation.
    """

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
        return {
            "error": "CALCULATION_FAILED",
            "message": str(error)
        }

def search_web(query):
    # TODO 2: Reuse your Lab 1 web-search implementation.
    # Return a concise string containing useful search results.
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        client = TavilyClient(api_key=tavily_api_key)
        search_results = client.search(query, search_depth="advanced")
        return str(search_results["results"][:3])
    except Exception as error:
        return {
            "error": "SEARCH_WEB_FAILED",
            "message": str(error)
        }

def get_stock_snapshot(ticker):
    key = ticker.upper().strip()
    if key not in MOCK_MARKET_DATA:
        # Explicit, structured, unambiguous. The model cannot mistake
        # this for a valid (if boring) snapshot.
        return {
            "error": "TICKER_NOT_FOUND",
            "message": f"'{key}' is not in the simulated market data set.",
            "valid_tickers": sorted(MOCK_MARKET_DATA.keys()),
        }
    return MOCK_MARKET_DATA[key]


def log_tool_call(step, tool_name, arguments, result, latency_ms, log_path="agent_trace.jsonl"):
    # TODO 1: Build one JSON-serializable record with every field
    # from the table above. Convert the timestamp with .isoformat()
    # first -- see the gotcha above.
    record = {
        "timestamp": datetime.now(),
        "step": step,
        "tool_name": tool_name,
        "arguments": arguments,
        "result": result,
        "latency_ms": latency_ms
    }


    # TODO 2: Append it as one line of JSON to log_path.
    # Use "a" mode so successive runs accumulate rather than overwrite.
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def build_windowed_context(all_steps, rolling_summary):
    # all_steps: the full list of {role, content, ...} messages generated
    # so far, grouped by ReAct step.

    # TODO 3: If len(all_steps) <= WINDOW_SIZE, no windowing is needed yet.
    # Return all_steps unchanged.
    if len(all_steps) <= WINDOW_SIZE:
        return all_steps

    # TODO 4: Otherwise, split into steps_to_summarize and steps_to_keep,
    # where steps_to_keep is the last WINDOW_SIZE steps.
    else:
        steps_to_summarize, steps_to_keep = all_steps[:-WINDOW_SIZE], all_steps[-WINDOW_SIZE:]

    # TODO 5: Fold steps_to_summarize into rolling_summary. You may do this
    # with a cheap-tier model call ("summarize these tool results in 2-3
    # sentences, preserving concrete numbers and ticker symbols exactly")
    # or with a deterministic Python summarizer that extracts key fields
    # (ticker, price, headline) without calling the model at all.
    summary_lines = []

    for message in steps_to_summarize:
        if message["role"] == "user":
            summary_lines.append(f"User request: {message['content']}")

        elif message["role"] == "tool":
            summary_lines.append(f"Tool result: {message['content']}")

    rolling_summary["content"] = ("Earlier observations:\n" + "\n".join(summary_lines))


    # TODO 6: Return [system_prompt, rolling_summary_message] + steps_to_keep.
    return [{"role": "system", "content": SYSTEM_PROMPT}, rolling_summary] + steps_to_keep



def build_messages(history, mode):
    # TODO 7: Return history + [{"role": "system", "content": PERSISTENT_CONSTRAINTS}]
    # so the reminder is always the last thing the model reads before
    # choosing its next action, regardless of how long history has grown.
    return history + [{"role": "system", "content": PERSISTENT_CONSTRAINTS}]


def check_model_drift(mode, tier, runtime_model):
    pinned = os.environ.get(
        f"{'OPENROUTER' if mode == 'online' else 'LOCAL_LLM'}_MODEL_{tier.upper()}"
    )

    # TODO 8: If pinned is None, warn that .env has no pin for this
    # tier at all -- there is nothing to drift-check against.

    # TODO 9: If pinned != runtime_model, print a loud WARNING naming
    # both values. Do not silently proceed as if they matched.

    # TODO 10: Call this once per tier, at startup, before the first
    # model request is made.
    pass



def main(args):
    load_dotenv()

    # TODO 3: Read the OpenRouter API key from the environment.
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    # TODO 4: Set the model. You may reuse the model you selected in Lab 1.
    model = args[0] if args else "openrouter/free"
    #"nvidia/nemotron-3-super-120b-a12b:free"


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
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Web search query."
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                },
                "required": ["query"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_stock_snapshot",
                "description": "Search the web for information needed to answer the user's question. Provide a concise search query describing the specific information you need.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Returns a structured price snapshot for one publicly traded ticker symbol from a fixed lookup table. Use this whenever the user asks about a specific ticker's current price, day change, or volume. Do not use this for company news or qualitative information — use search_web for that instead. If the ticker is not in the lookup table, this tool returns an explicit error object rather than a price. "
                        }
                    }
                },
                "required": ["ticker"]
            }
        },
        {
            "type": "function",
            "function": {
                "name": "final_answer",
                "description": (
                    "Submit the completed stock comparison and end the task. Use observed stock snapshots for prices and day changes. Compute each momentum_score using calculator before calling this tool."
                ),
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "comparison_table": {
                            "type": "array",
                            "description": "One comparison record per requested ticker.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ticker": {
                                        "type": "string"
                                    },
                                    "price": {
                                        "type": "number"
                                    },
                                    "day_change_pct": {
                                        "type": "number"
                                    },
                                    "momentum_score": {
                                        "type": "number",
                                        "description": (
                                            "The score computed using calculator "
                                            "with the lab's momentum formula."
                                        )
                                    }
                                },
                                "required": [
                                    "ticker",
                                    "price",
                                    "day_change_pct",
                                    "momentum_score"
                                ],
                                "additionalProperties": False
                            }
                        },
                        "winner": {
                            "type": "string",
                            "description": "The ticker selected as the winner."
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["low", "medium", "high"]
                        }
                    },
                    "required": [
                        "comparison_table",
                        "winner",
                        "confidence"
                    ],
                    "additionalProperties": False
                }
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

            start = time.perf_counter()
            if tool_name == "calculator":
                tool_result = calculator(arguments["expression"])

            elif tool_name == "search_web":
                tool_result = search_web(arguments["query"])

            elif tool_name == "get_stock_snapshot":
                tool_result = get_stock_snapshot(arguments["ticker"])

            elif tool_name == "final_answer":
                tool_result = arguments
                latency = (time.perf_counter() - start) * 1000

                print("FINAL ANSWER:")
                print(json.dumps(arguments, indent=2))

                log_tool_call(step, tool_name, arguments, tool_result, latency_ms)
                return
            else:
                tool_result = {"error": f"Unknown tool: {tool_name}"}

            latency_ms = (time.perf_counter() - start) * 1000
            log_tool_call(step, call["function"]["name"], arguments, tool_result, latency_ms)

            # TODO 11: Print the action and observation.
            print("ACTION:", tool_name, arguments)
            print("OBSERVATION:", tool_result)

            # TODO 12: Append the tool result to messages.
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": str(tool_result) if isinstance(tool_result, str) else json.dumps(tool_result)
            })

    else:
        print("\nAgent stopped: maximum step budget reached.")

if __name__ == "__main__":
    main(sys.argv[1:])