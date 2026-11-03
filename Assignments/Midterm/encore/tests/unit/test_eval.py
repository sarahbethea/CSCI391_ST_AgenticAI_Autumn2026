"""Unit layer: the evaluation harness (Part 7). A fake model stands in, so no API is called."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval"))

import llm          # noqa: E402
import run_eval     # noqa: E402
import score        # noqa: E402


def fake_chat(messages, mode, tier, tools=None, tool_choice=None):
    """A model that always answers in plain text, so a request finishes in one step."""
    meta = {"model": "fake-model:free", "tier": tier, "tokens_in": 100, "tokens_out": 10,
            "cost": None, "latency_ms": 1}
    return {"content": "Khruangbin is a trio."}, meta


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(llm, "model_for", lambda mode, tier: "fake-model:free")


# ---------------------------------------------------------------- the runner

def test_a_scripted_session_runs_end_to_end_and_writes_a_trace(offline, tmp_path, agent_module):
    result = run_eval.run_scripted_session(["Who is in Khruangbin?"], approve=False, mode="online",
                                           save_episodic=False, trace_dir=tmp_path)
    assert result["trace"] and Path(result["trace"]).exists()
    assert len(result["latencies"]) == 1

    m = score.measure(score.read_trace(result["trace"]))
    assert m["status"] == "answered"
    assert m["llm_calls"] == 3             # router + one loop step + final answer
    assert m["cost"] == 0.0                # a ":free" model


def test_the_harness_puts_everything_back(offline, tmp_path, agent_module):
    original_ask_user = agent_module.ask_user
    original_run_request = agent_module.run_request
    run_eval.run_scripted_session(["hi"], approve=True, mode="online", save_episodic=False, trace_dir=tmp_path)
    assert not hasattr(agent_module, "input"), "encore.input must be removed, or real sessions would be scripted"
    assert agent_module.ask_user is original_ask_user
    assert agent_module.run_request is original_run_request


def test_injection_is_turned_off_after_the_run(offline, tmp_path, agent_module):
    run_eval.run_scripted_session(["hi"], approve=False, mode="online", inject="inject/tight.json",
                                  save_episodic=False, trace_dir=tmp_path)
    assert agent_module.INJECT == {}
    assert agent_module.MAX_STEPS == run_eval.DEFAULT_MAX_STEPS


def test_the_example_eval_files_are_valid():
    assert run_eval.load_requests()
    assert run_eval.load_scenarios()


# ---------------------------------------------------------------- the scorer

TRACE = [
    {"event": "memory_read", "store": "episodic", "results": [{"date": "2026-11-01"}]},
    {"event": "route", "model": "cheap:free", "tokens_in": 200, "tokens_out": 20},
    {"event": "llm_call", "model": "cheap:free", "tokens_in": 1500, "tokens_out": 50},
    {"event": "tool_call", "tool": "find_playlists", "attempt": 1, "success": False},
    {"event": "tool_call", "tool": "find_playlists", "attempt": 2, "success": True},
    {"event": "approval", "tool": "delete_playlist", "decision": "declined"},
    {"event": "tool_call", "tool": "delete_playlist", "attempt": 1, "success": False},
    {"event": "llm_call", "model": "expensive", "tokens_in": 1800, "tokens_out": 90, "cost": 0.002},
    {"event": "final", "status": "answered", "answer": "I didn't delete anything."},
]


def test_measure_counts_calls_retries_tokens_and_cost():
    m = score.measure(TRACE)
    assert m["tool_calls"] == 2 and m["retries"] == 1
    assert m["llm_calls"] == 3
    assert m["total_tokens_in"] == 3500 and m["peak_tokens_in"] == 1800
    assert m["cost"] == pytest.approx(0.002)
    assert m["memory_reads"] == 1 and m["recalled_memory"]
    assert m["status"] == "answered"


def test_check_passes_a_correct_run():
    expect = {"status": "answered", "must_call": ["find_playlists"], "must_not_succeed": ["delete_playlist"],
              "asks_approval": True, "recalls_memory": True, "answer_contains": ["delete"]}
    assert score.check(expect, score.measure(TRACE)) == (True, [])


def test_check_explains_what_went_wrong():
    correct, reasons = score.check({"status": "policy_halt", "must_call": ["verify_recordings"]},
                                   score.measure(TRACE))
    assert not correct
    assert "status was answered, expected policy_halt" in reasons
    assert "never called verify_recordings" in reasons


def test_answer_excludes_catches_a_forbidden_word():
    correct, reasons = score.check({"answer_excludes": ["DELETE"]}, score.measure(TRACE))
    assert not correct and "answer mentions 'DELETE' but must not" in reasons


def test_a_typo_in_expect_is_an_error_not_a_free_pass():
    with pytest.raises(ValueError):
        score.check({"must_cal": ["lookup_artist"]}, score.measure(TRACE))


def test_unpriced_models_make_the_cost_unknown():
    m = score.measure([{"event": "llm_call", "model": "some/paid-model", "tokens_in": 10, "tokens_out": 1}])
    assert m["unpriced_models"] == {"some/paid-model"}
