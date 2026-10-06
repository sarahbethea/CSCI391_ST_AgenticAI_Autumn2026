import os
import sys
import requests
import json
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from tavily import TavilyClient


MAX_STEPS = 20
WINDOW_SIZE = 4
TIERING_ENABLED = True
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


MOCK_MARKET_DATA = {
    "NVDA": {"ticker": "NVDA", "price": 187.42, "day_change_pct": 2.1, "volume": 41200000},
    "AMD":  {"ticker": "AMD",  "price": 152.08, "day_change_pct": -0.8, "volume": 28950000},
    "INTC": {"ticker": "INTC", "price": 24.63,  "day_change_pct": 1.4, "volume": 55310000},
    "QCOM": {"ticker": "QCOM", "price": 168.91, "day_change_pct": 0.3, "volume": 9870000},
}

def calculator(expression):
    # TODO 1: Implement a simple calculator tool.
    # Return a string containing the calculation result.
    try:
        allowed_characters = "0123456789+-*/().% "

        if not all(char in allowed_characters for char in expression):
            return {
                "error": "INVALID_EXPRESSION",
                "message": "Expression contains invalid characters."
            }

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
        results = search_results["results"][:3]

        if not results:
            return {
                "error": "NO_SEARCH_RESULTS",
                "message": f"No results were found for query: {query}"
            }

        return json.dumps([
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": (item.get("content") or "")[:400]
            }
            for item in results
        ])

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

    # get indices of start of new step, determined by location of new model message. 
    step_starts = []
    for i, message in enumerate(all_steps):
        if message["role"] == "assistant":
            step_starts.append(i)
    if len(step_starts) <= WINDOW_SIZE:
        return [{"role": "system", "content": SYSTEM_PROMPT}] + all_steps

    # TODO 4: Otherwise, split into steps_to_summarize and steps_to_keep,
    # where steps_to_keep is the last WINDOW_SIZE steps.
    cutoff = step_starts[-WINDOW_SIZE]
    steps_to_summarize, steps_to_keep = all_steps[:cutoff], all_steps[cutoff:]

    print(
            f"WINDOWING: summarizing {len(step_starts) - WINDOW_SIZE} "
            f"older steps; keeping {WINDOW_SIZE} recent steps."
        )

    # TODO 5: Fold steps_to_summarize into rolling_summary. You may do this
    # with a cheap-tier model call ("summarize these tool results in 2-3
    # sentences, preserving concrete numbers and ticker symbols exactly")
    # or with a deterministic Python summarizer that extracts key fields
    # (ticker, price, headline) without calling the model at all.
    summary_lines = []
    calls_by_id = {}

    for message in steps_to_summarize:
        if message["role"] == "user":
            summary_lines.append(
                f"User request: {message['content']}"
            )

        elif message["role"] == "assistant":
            for call in message.get("tool_calls") or []:
                calls_by_id[call["id"]] = call["function"]

        elif message["role"] == "tool":
            call = calls_by_id[message["tool_call_id"]]
            tool_name = call["name"]
            arguments = call["arguments"]
            result = message["content"]

            if tool_name == "search_web":
                search_data = json.loads(result)

                # Successful searches return a list.
                # Error dictionaries stay intact.
                if isinstance(search_data, list):
                    result = json.dumps([
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", "")
                        }
                        for item in search_data
                    ])

            summary_lines.append(
                f"{tool_name}({arguments}) -> {result}"
            )

    rolling_summary["content"] = ("Earlier observations:\n" + "\n".join(summary_lines))


    # TODO 6: Return [system_prompt, rolling_summary_message] + steps_to_keep.
    return [{"role": "system", "content": SYSTEM_PROMPT}, rolling_summary] + steps_to_keep



def build_messages(history, mode):
    # TODO 7: Return history + [{"role": "system", "content": PERSISTENT_CONSTRAINTS}]
    # so the reminder is always the last thing the model reads before
    # choosing its next action, regardless of how long history has grown.
    print("REINJECTION: adding persistent constraints.")
    return history + [{"role": "system", "content": PERSISTENT_CONSTRAINTS}]


def check_model_drift(mode, tier, runtime_model):
    pinned = os.environ.get(
        f"{'OPENROUTER' if mode == 'online' else 'LOCAL_LLM'}_MODEL_{tier.upper()}"
    )

    # TODO 8: If pinned is None, warn that .env has no pin for this
    # tier at all -- there is nothing to drift-check against.
    if pinned is None:
        print("Warning: .env has no pin for this tier")
        return


    # TODO 9: If pinned != runtime_model, print a loud WARNING naming
    # both values. Do not silently proceed as if they matched.
    if pinned != runtime_model:
        print(f"WARNING!: pinned model: {pinned}, runtime model: {runtime_model}")


    # TODO 10: Call this once per tier, at startup, before the first
    # model request is made.

def final_answer(answer, comparison_table, winner, confidence):
    return {
        "answer": answer,
        "comparison_table": comparison_table,
        "winner": winner,
        "confidence": confidence
    }

def main(args):
    load_dotenv()

    # TODO 3: Read the OpenRouter API key from the environment.
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    # TODO 4: Set the model. You may reuse the model you selected in Lab 1.
    model = args[0] if args else "openrouter/free"
    #"nvidia/nemotron-3-super-120b-a12b:free"

    # Check model drift
    mode = args[0] if args else "online"
    prefix = "OPENROUTER" if mode == "online" else "LOCAL_LLM"
    cheap_model = os.getenv(f"{prefix}_MODEL_CHEAP")
    expensive_model = os.getenv(f"{prefix}_MODEL_EXPENSIVE")

    check_model_drift(mode, "cheap", cheap_model)
    check_model_drift(mode, "expensive", expensive_model)
    loop_model = cheap_model if TIERING_ENABLED else expensive_model



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
                "description": "Search the web for company news and qualitative information. Do not use this for the simulated stock prices, day changes, or volumes, use get_stock_snapshot instead.",
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
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_stock_snapshot",
                "description": "Returns a structured price snapshot for one publicly traded ticker symbol from a fixed lookup table. Use this whenever the user asks about a specific ticker's current price, day change, or volume. Do not use this for company news or qualitative information — use search_web for that instead. If the ticker is not in the lookup table, this tool returns an explicit error object rather than a price. ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol, such as NVDA or AMD."
                        }
                    },
                    "required": ["ticker"],
                    "additionalProperties": False
                }
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
                        },
                        "answer": {
                            "type": "string",
                            "description": "A written explanation of the comparison and selected winner."
                        }
                    },
                    "required": [
                        "answer",
                        "comparison_table",
                        "winner",
                        "confidence"
                    ],
                    "additionalProperties": False
                }
            }
        }
    ]

    all_steps = []
    rolling_summary = {"role": "system", "content": "(no steps summarized yet)"}

    user_input = input("What would you like me to research?\n")
    all_steps.append({"role": "user", "content": user_input})
    total_tokens = 0
    run_start = time.perf_counter()

    for step in range(1, MAX_STEPS + 1):

        print(f"\n--- STEP {step} ---")

        windowed = build_windowed_context(all_steps, rolling_summary)
        messages = build_messages(windowed, mode)

        # TODO 6: Send the current conversation to the model.
        # Include the system prompt and tool definitions.
        if mode == "online":
            url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
            headers = {
                "Authorization": (f"Bearer {openrouter_api_key}"),
                "Content-Type": "application/json"
            }
        else:
            url = os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:8080/v1/chat/completions")
            headers = {"Content-Type": "application/json"}

        payload = {
            "model": loop_model, #use cheap model to run loop, reserve expensive model for synthesis
            "messages": messages,
            "tools": tools,
            "parallel_tool_calls": False,
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
        
        total_tokens += response_data["usage"]["total_tokens"]

        message = response_data["choices"][0]["message"]
        tool_calls = message.get("tool_calls") or []
        print(json.dumps(message, indent=2))

        # TODO 8: If the model did not request a tool,
        # print its response and terminate the loop.
        # make sure if final_answer requested, then its passed off to expensive model
        requested_final_answer = any(
            call["function"]["name"] == "final_answer"
            for call in tool_calls
        )

        if not tool_calls or requested_final_answer:
            print(f"FINAL SYNTHESIS: using {expensive_model}")
            final_payload = {
                "model": expensive_model,
                "messages": messages,
                "tools": tools,
                "tool_choice": {
                    "type": "function",
                    "function": {"name": "final_answer"}
                },
                "parallel_tool_calls": False,
            }

            response = requests.post(
                url,
                headers=headers,
                json=final_payload
            )

            if not response.ok:
                print(response.status_code, response.text)
                return

            response_data = response.json()
            total_tokens += response_data["usage"]["total_tokens"]
            message = response_data["choices"][0]["message"]
            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                print("Expensive model returned no tool calls. should have called final_answer")
                return 

        # TODO 9: Append the model's message to the conversation.
        all_steps.append(message)

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
                tool_result = final_answer(answer=arguments["answer"], comparison_table=arguments["comparison_table"], winner=arguments["winner"], confidence=arguments["confidence"])
                latency_ms = (time.perf_counter() - start) * 1000

                print("FINAL ANSWER:")
                print(json.dumps(arguments, indent=2))

                print(f"TOTAL RUN TIME: {time.perf_counter() - run_start:.2f} seconds")
                print(f"TOTAL TOKENS: {total_tokens}")
                print(f"WINNER: {tool_result['winner']}")

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
            all_steps.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": str(tool_result) if isinstance(tool_result, str) else json.dumps(tool_result)
            })

    else:
        print("\nAgent stopped: maximum step budget reached without a final answer.")
        print(f"TOTAL RUN TIME: {time.perf_counter() - run_start:.2f} seconds")
        print(f"TOTAL TOKENS: {total_tokens}")

if __name__ == "__main__":
    main(sys.argv[1:])