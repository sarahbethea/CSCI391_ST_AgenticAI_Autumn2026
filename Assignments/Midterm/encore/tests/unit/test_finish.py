"""Unit layer: finish(), the single exit for a normal end of a request (Part 4). No real model is called."""

import json

import llm


def tool_call(arguments: dict) -> dict:
    return {"tool_calls": [{"id": "c1", "function": {"name": "final_answer", "arguments": json.dumps(arguments)}}]}


def test_a_rejected_final_answer_is_explained_to_the_next_model(agent_module, monkeypatch):
    # traces/20261102-180823_babcf911.jsonl: both models put delete_playlist's arguments into final_answer.
    seen = []

    def chat(messages, mode, tier, tools=None, tool_choice=None):
        seen.append(messages)
        meta = {"model": "fake", "tier": tier, "tokens_in": 1, "tokens_out": 1, "cost": 0, "latency_ms": 1}
        if tier == "expensive":
            return tool_call({"playlist_mbid": "3eb68a01"}), meta
        if "rejected" in messages[-1]["content"]:
            return tool_call({"status": "answered", "answer": "I deleted nothing.", "confidence": "high"}), meta
        return tool_call({"playlist_mbid": "3eb68a01"}), meta     # without the explanation, it repeats the mistake

    monkeypatch.setattr(llm, "chat", chat)
    status, answer = agent_module.finish([{"role": "user", "content": "Delete all my playlists."}], "online")

    assert status == "answered" and answer == "I deleted nothing."
    assert "playlist_mbid" in seen[1][-1]["content"], "the cheap model must be told why the first answer was rejected"
