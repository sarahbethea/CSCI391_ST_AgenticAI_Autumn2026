"""Unit layer: the hot-state store (working memory, Part 5.1). Uses a temporary database file."""

import pytest

import hot_state

USER = "test_user"
OTHER = "someone_else"


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    hot_state.close()
    monkeypatch.setattr(hot_state, "DB_PATH", tmp_path / "hot_state.db")
    yield
    hot_state.close()


def test_set_then_get_any_json_value():
    hot_state.set_value(USER, "active_playlist", {"playlist_mbid": "p1", "title": "[Encore] Focus"})
    hot_state.set_value(USER, "tool_call_count", 3)
    assert hot_state.get_value(USER, "active_playlist")["title"] == "[Encore] Focus"
    assert hot_state.get_value(USER, "tool_call_count") == 3
    assert hot_state.get_value(USER, "missing", default="nothing") == "nothing"


def test_setting_again_overwrites():
    hot_state.set_value(USER, "tool_call_count", 1)
    hot_state.set_value(USER, "tool_call_count", 2)
    assert hot_state.get_value(USER, "tool_call_count") == 2


def test_users_do_not_see_each_others_keys():
    hot_state.set_value(USER, "last_artist", {"name": "GUNSHIP"})
    assert hot_state.get_value(OTHER, "last_artist") is None


def test_expired_values_are_gone():
    hot_state.set_value(USER, "active_playlist", {"title": "old"}, ttl_s=-1)    # already expired
    assert hot_state.get_value(USER, "active_playlist") is None


def test_values_survive_a_restart():
    hot_state.set_value(USER, "active_playlist", {"title": "[Encore] Focus"})
    hot_state.close()                                                          # simulate restarting Encore
    assert hot_state.get_value(USER, "active_playlist") == {"title": "[Encore] Focus"}


def test_reset_session_keeps_carryover_keys():
    hot_state.set_value(USER, "verified_recordings", {"m1": {"title": "Tech Noir"}})
    hot_state.set_value(USER, "session_preferences", ["no Christmas music"])
    hot_state.set_value(USER, "active_playlist", {"title": "[Encore] Focus"})
    hot_state.reset_session(USER)
    assert hot_state.get_value(USER, "verified_recordings") is None, "verification is per session"
    assert hot_state.get_value(USER, "session_preferences") is None
    assert hot_state.get_value(USER, "active_playlist") == {"title": "[Encore] Focus"}


def test_forget_user_removes_everything_for_that_user_only():
    hot_state.set_value(USER, "active_playlist", {"title": "x"})
    hot_state.set_value(USER, "tool_call_count", 5)
    hot_state.set_value(OTHER, "tool_call_count", 9)
    assert hot_state.forget_user(USER) == 2
    assert hot_state.all_values(USER) == {}, "nothing may remain for the forgotten user"
    assert hot_state.get_value(OTHER, "tool_call_count") == 9, "other users are untouched"
