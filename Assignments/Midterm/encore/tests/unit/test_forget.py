"""Unit layer: hot state wired into the loop, and --forget leaving nothing behind (Part 5)."""

import json

import hot_state

PLAYLIST = {"success": True, "data": {"playlist_mbid": "p1", "title": "[Encore] Focus", "track_count": 1}}
ARTIST = {"success": True, "data": {"artist_mbid": "a1", "name": "GUNSHIP", "relations": []}}
SEARCH = {"success": True, "data": {"recordings": [
    {"recording_mbid": "m1", "title": "Tech Noir", "artist": "GUNSHIP", "length_s": 297}]}}


def fill_hot_state(enc):
    """What a short session would leave behind: a playlist, an artist, a verified song, a preference."""
    enc.remember_from_result("create_playlist", PLAYLIST)
    enc.remember_from_result("lookup_artist", ARTIST)
    enc.remember_from_result("search_recordings", SEARCH)
    enc.note_preference("no Christmas music")


def test_the_loop_records_hot_state_from_tool_results(agent_module):
    fill_hot_state(agent_module)
    state = hot_state.all_values(agent_module.ENCORE_USER_ID)
    assert state["active_playlist"]["title"] == "[Encore] Focus"
    assert state["last_artist"]["name"] == "GUNSHIP"
    assert "m1" in state["verified_recordings"]
    assert state["session_preferences"] == ["no Christmas music"]
    assert state["tool_call_count"] == 3


def test_failed_tool_results_are_not_remembered(agent_module):
    agent_module.remember_from_result("create_playlist", {"success": False, "data": None})
    assert hot_state.get_value(agent_module.ENCORE_USER_ID, "active_playlist") is None


def test_hot_state_reaches_every_model_call(agent_module):
    fill_hot_state(agent_module)
    messages = agent_module.build_messages("RULES", "GUIDANCE", "add it to that playlist", [])
    state_block = messages[3]["content"]
    assert "[Encore] Focus" in state_block and "p1" in state_block
    assert "no Christmas music" in state_block


def test_forget_leaves_nothing_behind(agent_module, capsys):
    fill_hot_state(agent_module)
    user = agent_module.ENCORE_USER_ID
    assert hot_state.all_values(user) != {}

    counts = agent_module.forget_user(user)

    assert counts["hot state"] == 5
    assert hot_state.all_values(user) == {}, "--forget must remove every item for the user"
    assert "item(s) deleted" in capsys.readouterr().out, "the counts must be printed"


def test_note_preference_does_not_duplicate(agent_module):
    agent_module.note_preference("no Christmas music")
    result = json.loads(agent_module.note_preference("no Christmas music"))
    assert result["data"]["session_preferences"] == ["no Christmas music"]
