"""Unit layer: session traces (Part 6). Each test writes to its own temporary folder."""

import json

import pytest

import tracer

FAKE_TOKEN = "lb-token-0123456789abcdef"


@pytest.fixture
def trace_dir(tmp_path, monkeypatch):
    """Start a session in a temp folder with a known fake token; close it afterwards."""
    monkeypatch.setenv("LISTENBRAINZ_TOKEN", FAKE_TOKEN)
    tracer.start_session(tmp_path)
    yield tmp_path
    tracer.end_session()


def read_lines(folder):
    files = list(folder.glob("*.jsonl"))
    assert len(files) == 1, "one session should make exactly one trace file"
    return [json.loads(line) for line in files[0].read_text().splitlines()]


def test_every_line_is_json_with_the_standard_fields(trace_dir):
    tracer.start_request()
    tracer.log("tool_call", tool="lb_radio", success=True)
    tracer.log("final", status="answered")
    lines = read_lines(trace_dir)
    assert [line["event"] for line in lines] == ["tool_call", "final"]
    for line in lines:
        assert line["ts"] and line["session_id"] and line["request_id"] == 1


def test_the_token_never_reaches_the_file(trace_dir):
    tracer.log("tool_call", args={"note": f"Token {FAKE_TOKEN}"}, message=f"failed with {FAKE_TOKEN}")
    text = next(trace_dir.glob("*.jsonl")).read_text()
    assert FAKE_TOKEN not in text
    assert tracer.REDACTED in text


def test_long_messages_are_shortened(trace_dir):
    tracer.log("tool_call", message="x" * 1000)
    message = read_lines(trace_dir)[0]["message"]
    assert len(message) < 400 and "more chars" in message


def test_requests_are_numbered(trace_dir):
    tracer.start_request()
    tracer.log("route")
    tracer.start_request()
    tracer.log("route")
    assert [line["request_id"] for line in read_lines(trace_dir)] == [1, 2]


def test_no_session_means_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tracer, "TRACE_DIR", tmp_path)
    tracer.end_session()
    tracer.log("tool_call", tool="anything")          # tracing is off: must do nothing
    assert list(tmp_path.glob("*.jsonl")) == []
