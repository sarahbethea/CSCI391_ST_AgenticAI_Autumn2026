"""Unit layer: the MusicBrainz read cache (Part 0, "every request is polite")."""

import pytest


@pytest.fixture
def cache_on(enc, monkeypatch, tmp_path):
    """Turn the cache on, in a temporary folder."""
    monkeypatch.setattr(enc, "CACHE_ENABLED", True)
    monkeypatch.setattr(enc, "CACHE_DIR", tmp_path)
    return enc


def test_off_by_default(enc, net, FakeResp):
    net.queue(FakeResp(200, {"id": "a"}), FakeResp(200, {"id": "a"}))
    enc.http("GET", f"{enc.MB_API}/artist/a")
    enc.http("GET", f"{enc.MB_API}/artist/a")
    assert len(net.calls) == 2


def test_a_repeated_musicbrainz_read_is_served_from_the_cache(cache_on, net, FakeResp):
    net.queue(FakeResp(200, {"id": "a", "name": "GUNSHIP"}))
    first = cache_on.http("GET", f"{cache_on.MB_API}/artist/a", params={"inc": "artist-rels"})
    second = cache_on.http("GET", f"{cache_on.MB_API}/artist/a", params={"inc": "artist-rels"})
    assert len(net.calls) == 1, "the second identical read must not reach the network"
    assert first[0] == second[0] == 200
    assert first[1] == second[1] == {"id": "a", "name": "GUNSHIP"}


def test_different_parameters_are_different_questions(cache_on, net, FakeResp):
    net.queue(FakeResp(200, {"n": 1}), FakeResp(200, {"n": 2}))
    cache_on.http("GET", f"{cache_on.MB_API}/recording", params={"query": "Black"})
    cache_on.http("GET", f"{cache_on.MB_API}/recording", params={"query": "Alive"})
    assert len(net.calls) == 2


def test_listenbrainz_is_never_cached(cache_on, net, FakeResp):
    net.queue(FakeResp(200, {"playlists": []}), FakeResp(200, {"playlists": [{"title": "new"}]}))
    cache_on.http("GET", f"{cache_on.LB_API}/user/me/playlists")
    _, second, _ = cache_on.http("GET", f"{cache_on.LB_API}/user/me/playlists")
    assert len(net.calls) == 2, "the user's data changes; a stale copy would break the duplicate check"
    assert second == {"playlists": [{"title": "new"}]}


def test_failures_are_never_cached(cache_on, net, FakeResp):
    net.queue(FakeResp(503, {"error": "busy"}), FakeResp(200, {"id": "a"}))
    cache_on.http("GET", f"{cache_on.MB_API}/artist/a")
    status, _, _ = cache_on.http("GET", f"{cache_on.MB_API}/artist/a")
    assert status == 200, "a 503 must not be remembered"


def test_old_entries_are_fetched_again(cache_on, net, FakeResp, monkeypatch):
    net.queue(FakeResp(200, {"v": "old"}), FakeResp(200, {"v": "new"}))
    cache_on.http("GET", f"{cache_on.MB_API}/artist/a")
    monkeypatch.setattr(cache_on, "CACHE_MAX_AGE_S", -1)          # everything counts as expired
    _, body, _ = cache_on.http("GET", f"{cache_on.MB_API}/artist/a")
    assert body == {"v": "new"}
