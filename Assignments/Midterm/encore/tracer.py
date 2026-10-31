"""
Session traces (Part 6): one JSONL file per session in traces/, one line per event.

    tracer.start_session()            once, when a session begins
    tracer.start_request()            once per user request (numbers them 1, 2, 3...)
    tracer.log("tool_call", tool=...) anywhere something worth recording happens
    tracer.end_session()              once, when the session ends

"If it isn't in the trace, it didn't happen": graders, the workbook, and the evaluation
harness all read these files. Imports nothing from encore.py (a leaf module).
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

TRACE_DIR = Path(__file__).parent / "traces"
MAX_MESSAGE_CHARS = 300      # long messages are shortened: traces record what happened, not whole payloads
REDACTED = "[REDACTED]"

# The state of the current session. There is one session per run of Encore, so module-level
# variables are enough. While _trace_file is None, tracing is OFF and log() does nothing:
# that keeps unit tests (which never start a session) from writing files into traces/.
_trace_file = None
_session_id = None
_request_id = 0


def start_session(trace_dir: Path = TRACE_DIR) -> str:
    """Open a new trace file for this session and return the session ID."""
    global _trace_file, _session_id, _request_id

    # A short random ID tells sessions apart; the timestamp makes the files sort by time.
    _session_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    trace_dir.mkdir(parents=True, exist_ok=True)
    path = trace_dir / f"{timestamp}_{_session_id}.jsonl"

    # "a" = append: each event is added to the end of the file as it happens.
    _trace_file = open(path, "a", encoding="utf-8")
    _request_id = 0
    return _session_id


def start_request() -> int:
    """Number the next user request, so every event can say which request it belongs to."""
    global _request_id
    _request_id += 1
    return _request_id


def end_session() -> None:
    """Close the trace file. Logging after this does nothing until the next start_session()."""
    global _trace_file
    if _trace_file is not None:
        _trace_file.close()
        _trace_file = None


def scrub(text: str) -> str:
    """Replace every secret in the text with [REDACTED].

    The token should never reach a trace in the first place (we never log request headers).
    This is the safety net in case a future bug passes it into some field anyway: every line
    goes through here, so a secret is caught no matter which field it hid in.
    """
    # Read the secrets at call time, so the values loaded from .env are used.
    secrets = [os.getenv("LISTENBRAINZ_TOKEN"), os.getenv("OPENROUTER_API_KEY")]

    for secret in secrets:
        if secret and len(secret) >= 8:
            # Skip missing or very short values: scrubbing "" or "abc" would mangle normal text.
            text = text.replace(secret, REDACTED)
    return text


def log(event: str, **fields) -> None:
    """Append one event to the trace file, e.g. log("tool_call", tool="lb_radio", success=True)."""
    if _trace_file is None:
        # Tracing is off (no session started, e.g. in unit tests): do nothing.
        return

    # Shorten long messages: a trace line should say what happened, not copy a whole result.
    message = fields.get("message")
    if isinstance(message, str) and len(message) > MAX_MESSAGE_CHARS:
        extra = len(message) - MAX_MESSAGE_CHARS
        fields["message"] = message[:MAX_MESSAGE_CHARS] + f"... ({extra} more chars)"

    # Every line starts with the same identifying fields, then whatever the caller passed.
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": _session_id,
        "request_id": _request_id,
        "event": event,
    }
    record.update(fields)

    # Turn it into one line of JSON. default=str converts anything JSON can't handle
    # (a Path, an exception) into text instead of crashing the agent.
    line = json.dumps(record, ensure_ascii=False, default=str)

    # Remove secrets from the finished line, so no field can smuggle one through.
    line = scrub(line)

    # Write the line and flush it to disk right away: if Encore crashes a moment later,
    # every event up to the crash is already saved.
    _trace_file.write(line + "\n")
    _trace_file.flush()
