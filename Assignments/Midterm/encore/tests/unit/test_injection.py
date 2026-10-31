"""Unit layer: --inject fault injection (Part 7). No network: injected calls never reach it."""

import json

import pytest


@pytest.fixture
def inject(enc, monkeypatch, tmp_path):
    """Returns a function that loads a recipe; injection settings are reset after each test."""
    monkeypatch.setattr(enc, "INJECT", {})
    monkeypatch.setattr(enc, "MAX_STEPS", enc.MAX_STEPS)

    def load(recipe):
        path = tmp_path / "recipe.json"
        path.write_text(json.dumps(recipe))
        enc.load_injection(str(path))

    return load


def test_off_by_default(enc):
    assert enc.injected_failure(f"{enc.MB_API}/artist") is None


def test_same_seed_gives_the_same_failures(enc, inject):
    inject({"transient_rate": 0.3, "seed": 7})
    first = [enc.injected_failure(f"{enc.MB_API}/x") for _ in range(20)]
    inject({"transient_rate": 0.3, "seed": 7})
    second = [enc.injected_failure(f"{enc.MB_API}/x") for _ in range(20)]
    assert first == second
    assert 503 in first and None in first, "a 0.3 rate should fail some calls and pass others"


def test_each_service_fails_with_its_own_code(enc, inject):
    inject({"transient_rate": 1.0})
    assert enc.injected_failure(f"{enc.LB_API}/user/x/listens") == 429
    assert enc.injected_failure(f"{enc.MB_API}/recording") == 503


def test_injected_call_never_reaches_the_network(enc, inject, net):
    inject({"transient_rate": 1.0})
    status, body, _ = enc.http("GET", f"{enc.MB_API}/recording")
    assert (status, body) == (503, "injected")
    assert net.calls == [], "an injected failure must not send a real request"


def test_outage_becomes_fatal_after_retries(enc, inject, net):
    inject({"transient_rate": 1.0})
    result = json.loads(enc.call_tool_with_retry("search_recordings", '{"title": "Black"}', {"search_recordings"}))
    assert result["error_category"] == "fatal"
    assert net.calls == []


def test_max_steps_override(enc, inject):
    inject({"max_steps": 2})
    assert enc.MAX_STEPS == 2


def test_bad_rate_is_rejected(enc, inject):
    with pytest.raises(ValueError):
        inject({"transient_rate": 1.5})
