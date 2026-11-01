"""Unit layer: the approval gate (Part 4). Approval lives in the loop, so it is tested without a model."""

import builtins

import pytest


@pytest.mark.parametrize("name, arguments, request_text, expected", [
    ("get_feedback", {}, "what do I love?", False),                                     # reads never ask
    ("delete_playlist", {"playlist_mbid": "x"}, "delete it", True),                   # always asks
    ("export_playlist", {"service": "spotify"}, "export to spotify", True),           # always asks
    ("create_playlist", {"title": "Focus"}, "create a focus playlist", True),         # the user hasn't seen the songs
    ("set_feedback", {"action": "love"}, "love the second song", False),              # named this exact action
    ("set_feedback", {"action": "hate"}, "love the second song", True),               # a different action: ask
])
def test_needs_approval(agent_module, name, arguments, request_text, expected):
    assert agent_module.needs_approval(name, arguments, request_text) is expected


@pytest.mark.parametrize("typed, expected", [
    ("y", True), ("YES", True), (" yes ", True),
    ("", False), ("n", False), ("sure", False), ("yy", False),                        # anything else is a no
])
def test_ask_user_fails_closed(agent_module, monkeypatch, typed, expected):
    monkeypatch.setattr(builtins, "input", lambda prompt="": typed)
    assert agent_module.ask_user("summary") is expected


def test_no_one_to_answer_means_no(agent_module, monkeypatch):
    def closed_input(prompt=""):
        raise EOFError
    monkeypatch.setattr(builtins, "input", closed_input)
    assert agent_module.ask_user("summary") is False


@pytest.fixture
def stubborn_model(agent_module, monkeypatch):
    """A fake model that asks for the same playlist write twice, then replies in text.

    Returns the list of summaries the user was asked about.
    """
    write = {"id": "c1", "type": "function",
             "function": {"name": "create_playlist", "arguments": '{"title": "Focus", "recording_mbids": ["m1"]}'}}
    replies = {"count": 0}

    def fake_chat(messages, mode, tier, tools=None, tool_choice=None):
        replies["count"] += 1
        if replies["count"] <= 2:
            return {"role": "assistant", "content": "", "tool_calls": [dict(write, id=f"c{replies['count']}")]}, {}
        return {"role": "assistant", "content": "OK, I did not create it."}, {}

    asked = []
    monkeypatch.setattr(agent_module.router, "route",
                        lambda request, mode: {"domains": ["library"], "fallback": False, "error": None, "meta": {}})
    monkeypatch.setattr(agent_module.llm, "chat", fake_chat)
    monkeypatch.setattr(agent_module, "ask_user", lambda summary: asked.append(summary) or False)   # always "no"
    monkeypatch.setattr(agent_module, "describe_write", lambda name, arguments: f"summary of {name}")
    return asked, replies


def test_a_declined_write_is_not_asked_twice(agent_module, stubborn_model):
    asked, _ = stubborn_model
    history = []
    status, answer = agent_module.run_request("make me a focus playlist", history, "RULES", "GUIDANCE", "online")
    assert len(asked) == 1, "the second identical request must be declined without asking"
    tool_results = [m["content"] for m in history if m["role"] == "tool"]
    assert "already declined" in tool_results[1]


def test_a_new_request_asks_again(agent_module, stubborn_model):
    asked, replies = stubborn_model
    history = []
    agent_module.run_request("make me a focus playlist", history, "RULES", "GUIDANCE", "online")
    replies["count"] = 0                                    # the model asks for the same write in a new request
    agent_module.run_request("ok, actually create it", history, "RULES", "GUIDANCE", "online")
    assert len(asked) == 2, "declines only last for the request they happened in"


def test_summary_shows_song_titles_not_ids(agent_module):
    agent_module.add_verified([{"recording_mbid": "m1", "title": "Tech Noir", "artist": "GUNSHIP", "length_s": 300}])
    summary = agent_module.describe_write("create_playlist", {"title": "Focus", "recording_mbids": ["m1"]})
    assert "Tech Noir — GUNSHIP" in summary
    assert "[Encore] Focus" in summary
    assert "about 5 min" in summary
