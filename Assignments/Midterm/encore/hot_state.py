"""
Hot state: the small, frequently read part of working memory (Part 5.1), adapted from
memory_examples/ch07_06_sqlite_hot_store.py.

A key-value store in one SQLite file. Every row is scoped by (user_id, key), so each user has
their own namespace and forget_user() can delete everything for one user (the --forget path).

    hot_state.set_value(user, "active_playlist", {...}, ttl_s=hot_state.CARRYOVER_TTL_S)
    hot_state.get_value(user, "active_playlist")             -> the value, or None
    hot_state.reset_session(user)                            at session start
    hot_state.forget_user(user)                              -> how many rows were deleted

Unlike the conversation history, hot state is never summarized away: the loop rebuilds it into
every model call. Imports nothing from encore.py (a leaf module).
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

# memory/ is in .gitignore: memory stores must never be committed (Part 10).
DB_PATH = Path(__file__).parent / "memory" / "hot_state.db"

# Keys that belong to ONE session and are cleared when a new session starts.
#   verified_recordings: the spec says MBIDs must be verified "in this session"
#   session_preferences: later sessions learn preferences through episodic memory instead
#   tool_call_count:     a per-session counter
SESSION_KEYS = ("verified_recordings", "session_preferences", "tool_call_count")

# Keys like active_playlist and last_recording survive a restart for a day, so "add it to that
# playlist" still works after restarting Encore, without stale references lingering for weeks.
CARRYOVER_TTL_S = 24 * 3600

# One shared connection, opened the first time it is needed.
_conn = None


def _connection() -> sqlite3.Connection:
    """Open the database (creating the file and table if needed) and reuse the connection."""
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH)
        # One table. The primary key (user_id, key) means each user has their own keys,
        # and setting the same key again replaces the old value.
        _conn.execute(
            """
            CREATE TABLE IF NOT EXISTS hot_state (
                user_id    TEXT NOT NULL,
                key        TEXT NOT NULL,
                value      TEXT NOT NULL,   -- JSON
                expires_at REAL,            -- unix time; NULL = never expires
                PRIMARY KEY (user_id, key)
            )
            """
        )
        _conn.commit()
    return _conn


def close() -> None:
    """Close the connection (tests use this to switch to a temporary database file)."""
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def set_value(user_id: str, key: str, value: Any, ttl_s: float | None = None) -> None:
    """Store any JSON-serializable value under (user_id, key). Overwrites the old value."""
    if ttl_s is None:
        expires_at = None
    else:
        expires_at = time.time() + ttl_s
    conn = _connection()
    conn.execute(
        "INSERT OR REPLACE INTO hot_state VALUES (?, ?, ?, ?)",
        (user_id, key, json.dumps(value), expires_at),
    )
    conn.commit()


def get_value(user_id: str, key: str, default: Any = None) -> Any:
    """Return the stored value, or the default if the key is missing or has expired."""
    row = _connection().execute(
        "SELECT value, expires_at FROM hot_state WHERE user_id = ? AND key = ?",
        (user_id, key),
    ).fetchone()

    if row is None:
        return default

    value, expires_at = row
    if expires_at is not None and expires_at < time.time():
        # Expired: clean it up now, and behave as if it were never there.
        delete_value(user_id, key)
        return default

    return json.loads(value)


def delete_value(user_id: str, key: str) -> None:
    """Remove one key for one user."""
    conn = _connection()
    conn.execute("DELETE FROM hot_state WHERE user_id = ? AND key = ?", (user_id, key))
    conn.commit()


def all_values(user_id: str) -> dict:
    """Every live (unexpired) key and value for one user. Useful for inspecting and testing."""
    rows = _connection().execute(
        "SELECT key FROM hot_state WHERE user_id = ?", (user_id,)
    ).fetchall()
    values = {}
    for (key,) in rows:
        value = get_value(user_id, key)       # get_value skips and cleans up expired keys
        if value is not None:
            values[key] = value
    return values


def reset_session(user_id: str) -> int:
    """At session start: clear the keys that belong to one session. Returns how many were removed."""
    conn = _connection()
    removed = 0
    for key in SESSION_KEYS:
        cursor = conn.execute("DELETE FROM hot_state WHERE user_id = ? AND key = ?", (user_id, key))
        removed += cursor.rowcount
    conn.commit()
    return removed


def forget_user(user_id: str) -> int:
    """Privacy path (--forget): delete EVERYTHING stored for one user. Returns the count deleted."""
    conn = _connection()
    cursor = conn.execute("DELETE FROM hot_state WHERE user_id = ?", (user_id,))
    conn.commit()
    return cursor.rowcount
