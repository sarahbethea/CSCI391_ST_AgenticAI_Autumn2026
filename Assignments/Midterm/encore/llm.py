"""
One way to call a model, for every caller (router, loop, summarizer, quality check, final_answer).
Callers build the messages; this module picks the model and measures the call. Imports nothing from encore.py.
"""

import os
import random
import time

import requests
from dotenv import load_dotenv

load_dotenv()

LLM_TIMEOUT_S = 120     # free-tier and local models can be slow; this is the model, not ListenBrainz
MAX_RETRIES = 3         # short on purpose: a used-up daily limit (also 429) won't clear by waiting


def _retryable(err: requests.RequestException) -> bool:
    """Worth trying again? Same rule as classify_status for tools: 408/429 and 5xx, or no response at all."""
    if isinstance(err, requests.HTTPError):
        status = err.response.status_code
        if status in (408, 429) or status >= 500:
            return True      # rate-limited, timed out, or a server error
        else:
            return False     # 400, 401, 402, 403, 404: our request is the problem
    else:
        if isinstance(err, (requests.ConnectionError, requests.Timeout)):
            return True      # no response at all: the network or the server hiccuped
        else:
            return False     # a malformed URL or similar: a config bug


def model_for(mode: str, tier: str) -> str:
    """The pinned model string for this mode and tier, from .env (Lab 3 tiering)."""
    prefix = "OPENROUTER" if mode == "online" else "LOCAL_LLM"
    model = os.getenv(f"{prefix}_MODEL_{tier.upper()}")
    if not model:
        raise RuntimeError(f"{prefix}_MODEL_{tier.upper()} is not set in .env")
    return model


def chat(messages: list[dict], mode: str, tier: str, tools: list[dict] | None = None,
         tool_choice=None) -> tuple[dict, dict]:
    """Send messages to the model. Returns (assistant message, meta for the trace)."""
    model = model_for(mode, tier)
    if mode == "online":
        url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
    else:
        url = os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:8080/v1/chat/completions")
        headers = {}
    payload = {"model": model, "messages": messages, "temperature": 0}
    if tools:
        payload["tools"] = tools
        payload["parallel_tool_calls"] = False     # one tool per step keeps approval and traces simple
        if tool_choice:
            payload["tool_choice"] = tool_choice

    start = time.monotonic()
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=LLM_TIMEOUT_S)
            response.raise_for_status()
            break
        except requests.RequestException as err:
            if attempt == MAX_RETRIES or not _retryable(err):
                raise                                   # the caller (or the session safety net) handles it
            delay = random.uniform(0, 2 ** attempt)     # full jitter: 0-1 s, 0-2 s, 0-4 s
            print(f"    model call failed ({err}); retrying in {delay:.1f}s")
            time.sleep(delay)

    body = response.json()
    usage = body.get("usage") or {}
    meta = {
        "model": body.get("model", model),      # what actually ran, for version pinning
        "tier": tier,
        "tokens_in": usage.get("prompt_tokens"),
        "tokens_out": usage.get("completion_tokens"),
        "cost": usage.get("cost"),              # USD, when OpenRouter reports it (None otherwise)
        "latency_ms": round((time.monotonic() - start) * 1000),
    }
    return body["choices"][0]["message"], meta
