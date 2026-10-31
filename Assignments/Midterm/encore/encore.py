"""
Encore -- a ListenBrainz music agent that remembers.   (CSCI 391 midterm starter)

    python encore.py <online|offline>             # interactive session
    python encore.py <online|offline> --forget    # delete every memory for ENCORE_USER_ID

Copy chat() and model_for() from your Lab 3 agent and your router from Lab 4.
"""

import argparse
import json
import os
import random
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

import llm
import router

load_dotenv()

LB_API = "https://api.listenbrainz.org/1"
MB_API = "https://musicbrainz.org/ws/2"
LB_TOKEN = os.getenv("LISTENBRAINZ_TOKEN")        # never log or store this
LB_USER = os.getenv("LISTENBRAINZ_USER")
ENCORE_USER_ID = os.getenv("ENCORE_USER_ID", LB_USER)  # deletion key for all memory
USER_AGENT = f"Encore-CSCI391/0.1 ( {os.getenv('CONTACT_EMAIL', 'you@umontana.edu')} )"

MAX_STEPS = 12          # bounded loop (Lab 2)
READ_TIMEOUT_S = 5
WRITE_TIMEOUT_S = 15
SLOW_READ_TIMEOUT_S = 15  # override for reads measured to be slow (ListenBrainz listens)
MB_MIN_INTERVAL_S = 1.5  # MusicBrainz allows about 1 request/second per IP; leave headroom

_last_mb_call = 0.0
_lb_wait_until = 0.0

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
RADIO_MODES = ("easy", "medium", "hard")
MAX_VERIFY = 25          # MBIDs per verify_recordings call (one MusicBrainz search)

# Recording MBIDs confirmed by verify_recordings this session. Playlist writes check it.
# TODO: move into hot state (Part 5.1) once that store exists.
VERIFIED_MBIDS: set[str] = set()


@dataclass
class ToolResult:                      # same contract as the Chapter 6 examples
    success: bool
    data: Optional[Any]
    error: Optional[str]
    error_category: Optional[str]      # "transient" | "input" | "resource" | "fatal"

    def to_json(self) -> str:
        return json.dumps(asdict(self))


def ok(data: Any) -> ToolResult:
    return ToolResult(True, data, None, None)


def fail(category: str, message: str) -> ToolResult:
    return ToolResult(False, None, message, category)


def classify_status(status: int) -> str:
    if status == 0 or status == 429 or status >= 500:
        return "transient"
    if status in (401, 403):
        return "fatal"
    if status == 404:
        return "resource"
    return "input"


# ---------------------------------------------------------------- fault injection (Part 7)

# Filled in by load_injection() when Encore runs with --inject <file.json>. Empty means "off",
# so normal runs and the unit tests behave exactly as before.
INJECT: dict = {}

# A random number generator used ONLY for injection. backoff_delays() also draws random numbers
# (for jitter); if they shared one generator, every retry would shift which later calls fail,
# and the same inject file would no longer give the same failures on every run.
_inject_rng = random.Random()


def load_injection(path: str) -> None:
    """Read a failure recipe such as {"transient_rate": 0.3, "max_steps": 4, "seed": 391}."""
    global MAX_STEPS

    with open(path, encoding="utf-8") as f:
        recipe = json.load(f)

    # transient_rate: the chance (0 to 1) that each ListenBrainz/MusicBrainz call fails.
    rate = recipe.get("transient_rate", 0.0)
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"transient_rate must be between 0 and 1; got {rate}")
    INJECT["transient_rate"] = rate

    # seed: makes the "random" failures repeat exactly on every run with the same file.
    _inject_rng.seed(recipe.get("seed", 391))

    # max_steps: replaces the normal step limit, to trigger budget_exceeded on purpose.
    if "max_steps" in recipe:
        if recipe["max_steps"] < 1:
            raise ValueError(f"max_steps must be at least 1; got {recipe['max_steps']}")
        MAX_STEPS = recipe["max_steps"]

    print(f"FAULT INJECTION ON: {recipe}")


def injected_failure(url: str) -> Optional[int]:
    """Should this request fail on purpose? Returns the fake status code, or None to send it for real."""
    rate = INJECT.get("transient_rate", 0.0)

    if rate == 0.0:
        # Injection is off (the normal case).
        return None

    if not (url.startswith(LB_API) or url.startswith(MB_API)):
        # Only the music APIs are injected, never anything else.
        return None

    # Roll a number between 0 and 1. Below the rate means "fail this call".
    roll = _inject_rng.random()
    if roll >= rate:
        return None

    # Fail the way each service really does when it is overloaded or rate limiting.
    if url.startswith(LB_API):
        return 429      # ListenBrainz: Too Many Requests
    else:
        return 503      # MusicBrainz: Service Unavailable


def http(method: str, url: str, *, params=None, body=None, auth=False, timeout=READ_TIMEOUT_S):
    """One polite request. Returns (status, json_or_text, headers). Status 0 = no response."""
    global _last_mb_call, _lb_wait_until

    # Fault injection: fail BEFORE reaching the network, so everything above http()
    # (the tool, classify_status, the retry wrapper, the loop) runs exactly as for a real failure.
    fake_status = injected_failure(url)
    if fake_status is not None:
        return fake_status, "injected", {}

    if url.startswith(MB_API):
        wait = _last_mb_call + MB_MIN_INTERVAL_S - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_mb_call = time.monotonic()
        params = {**(params or {}), "fmt": "json"}
    elif url.startswith(LB_API):
        wait = _lb_wait_until - time.monotonic()
        if wait > 0:                                  # honor the server's rate-limit headers
            time.sleep(wait)
    headers = {"User-Agent": USER_AGENT}
    if auth:
        headers["Authorization"] = f"Token {LB_TOKEN}"
    try:
        r = requests.request(method, url, params=params, json=body, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        return 0, f"{type(exc).__name__}", {}
    if url.startswith(LB_API) and r.headers.get("X-RateLimit-Remaining") == "0":
        _lb_wait_until = time.monotonic() + float(r.headers.get("X-RateLimit-Reset-In", "1"))
    try:
        return r.status_code, r.json(), r.headers
    except ValueError:
        return r.status_code, r.text, r.headers


# ---------------------------------------------------------------- worked examples

def get_recent_listens(count: int = 25) -> str:
    if not 1 <= count <= 100:
        return fail("input", f"count must be between 1 and 100; got {count}.").to_json()
    status, body, _ = http("GET", f"{LB_API}/user/{LB_USER}/listens", params={"count": count},
                           timeout=SLOW_READ_TIMEOUT_S)
    if status != 200:
        return fail(classify_status(status), f"ListenBrainz listens request failed (HTTP {status}).").to_json()
    listens = []
    for item in body["payload"]["listens"]:
        meta = item["track_metadata"]
        listens.append({
            "listened_at": item["listened_at"],
            "artist": meta.get("artist_name"),
            "track": meta.get("track_name"),
            "recording_mbid": (meta.get("mbid_mapping") or {}).get("recording_mbid"),
        })
    return ok({"listens": listens}).to_json()


def search_recordings(title: str, artist: str = "", limit: int = 5) -> str:
    if not title.strip():
        return fail("input", "title must not be empty.").to_json()
    query = f'recording:"{title}"' + (f' AND artist:"{artist}"' if artist else "")
    status, body, _ = http("GET", f"{MB_API}/recording", params={"query": query, "limit": limit})
    if status != 200:
        return fail(classify_status(status), f"MusicBrainz search failed (HTTP {status}).").to_json()
    hits = [{
        "recording_mbid": r["id"],
        "title": r["title"],
        "artist": "".join(c["name"] + c.get("joinphrase", "") for c in r.get("artist-credit", [])),
        "length_s": (r.get("length") or 0) // 1000,
        "first_release": r.get("first-release-date"),
    } for r in body.get("recordings", [])]
    if not hits:
        return fail("resource", f"No MusicBrainz recording matches '{title}'"
                                f"{' by ' + artist if artist else ''}.").to_json()
    return ok({"recordings": hits}).to_json()


FEEDBACK_SCORES = {"loved": 1, "hated": -1}
def get_feedback(kind: str = "loved", count: int = 25) -> str:
    if kind not in FEEDBACK_SCORES:
        return fail("input", f"kind must be 'loved' or 'hated'; got '{kind}'.").to_json()
    if not 1 <= count <= 100:
        return fail("input", f"count must be between 1 and 100; got {count}.").to_json()
    status, body, _ = http("GET", f"{LB_API}/feedback/user/{LB_USER}/get-feedback",
                           params={"score": FEEDBACK_SCORES[kind], "count": count, "metadata": "true"})
    if status != 200:
        return fail(classify_status(status), f"ListenBrainz feedback request failed (HTTP {status}).").to_json()
    recordings = []
    for item in body["feedback"]:
        meta = item.get("track_metadata") or {}
        recordings.append({
            "recording_mbid": item.get("recording_mbid"),
            "track": meta.get("track_name"),
            "artist": meta.get("artist_name"),
            "artist_mbids": (meta.get("mbid_mapping") or {}).get("artist_mbids", []),
        })
    if not recordings:
        return fail("resource", f"The user has no {kind} recordings on ListenBrainz.").to_json()
    return ok({"kind": kind, "total": body["total_count"], "recordings": recordings}).to_json()


FEEDBACK_ACTIONS = {"love": 1, "hate": -1, "clear": 0}
def set_feedback(recording_mbid: str, action: str) -> str:
    if not UUID_RE.match(recording_mbid or ""):
        return fail("input", f"recording_mbid must be a MusicBrainz recording UUID; got '{recording_mbid}'. "
                             "If you don't have one, call search_recordings first.").to_json()
    if action not in FEEDBACK_ACTIONS:
        return fail("input", f"action must be 'love', 'hate', or 'clear'; got '{action}'.").to_json()
    status, body, _ = http("POST", f"{LB_API}/feedback/recording-feedback",
                           body={"recording_mbid": recording_mbid, "score": FEEDBACK_ACTIONS[action]},
                           auth=True, timeout=WRITE_TIMEOUT_S)
    if status != 200:
        return fail(classify_status(status), f"ListenBrainz feedback write failed (HTTP {status}).").to_json()
    return ok({"recording_mbid": recording_mbid, "action": action}).to_json()
   
    

def lookup_artist(artist_mbid: str = "", name: str = "") -> str:
    if not artist_mbid and not name.strip():
        return fail("input", "Pass artist_mbid or name.").to_json()

    # Step 1: no MBID yet? Find one by name.
    if not artist_mbid:
        status, body, _ = http("GET", f"{MB_API}/artist", params={"query": f'artist:"{name}"', "limit": 1})
        if status != 200:
            return fail(classify_status(status), f"MusicBrainz artist search failed (HTTP {status}).").to_json()
        if not body.get("artists"):
            return fail("resource", f"No MusicBrainz artist matches '{name}'.").to_json()
        artist_mbid = body["artists"][0]["id"]

    # Step 2: look up by MBID (same code no matter how we got the MBID).
    if not UUID_RE.match(artist_mbid):
        return fail("input", f"artist_mbid must be a MusicBrainz artist UUID; got '{artist_mbid}'.").to_json()
    status, body, _ = http("GET", f"{MB_API}/artist/{artist_mbid}", params={"inc": "artist-rels"})
    if status != 200:
        return fail(classify_status(status), f"MusicBrainz artist lookup failed (HTTP {status}).").to_json()

    relations = [{
        "type": rel["type"],
        "direction": rel.get("direction"),
        "name": rel["artist"]["name"],
        "artist_mbid": rel["artist"]["id"],
        "attributes": rel.get("attributes", []),
        "begin": rel.get("begin"),
        "end": rel.get("end"),
    } for rel in body.get("relations", []) if rel.get("artist")]

    return ok({
        "artist_mbid": body["id"],
        "name": body["name"],
        "type": body.get("type"),
        "disambiguation": body.get("disambiguation"),
        "relations": relations,
    }).to_json()
    


def get_top_recordings_for_artist(artist_mbid: str, limit: int = 10) -> str:
    if not UUID_RE.match(artist_mbid or ""):
        return fail("input", f"artist_mbid must be a MusicBrainz artist UUID; got '{artist_mbid}'. "
                             "If you only have a name, call lookup_artist first.").to_json()
    if not 1 <= limit <= 50:
        return fail("input", f"limit must be between 1 and 50; got {limit}.").to_json()
    status, body, _ = http("GET", f"{LB_API}/popularity/top-recordings-for-artist/{artist_mbid}", auth=True)
    if status != 200:
        return fail(classify_status(status), f"ListenBrainz popularity request failed (HTTP {status}).").to_json()
    recordings = [{                                   # the response is a bare list, most-listened first
        "recording_mbid": r["recording_mbid"],
        "title": r.get("recording_name"),
        "artist": r.get("artist_name"),
        "length_s": (r.get("length") or 0) // 1000,
        "listen_count": r.get("total_listen_count"),
    } for r in body[:limit]]
    if not recordings:
        return fail("resource", f"ListenBrainz has no popularity data for artist {artist_mbid}.").to_json()
    return ok({"artist_mbid": artist_mbid, "recordings": recordings}).to_json()


def verify_recordings(recording_mbids: list[str]) -> str:
    if not recording_mbids or len(recording_mbids) > MAX_VERIFY:
        return fail("input", f"Pass 1 to {MAX_VERIFY} recording MBIDs; got {len(recording_mbids or [])}.").to_json()
    malformed = [m for m in recording_mbids if not UUID_RE.match(m or "")]
    if malformed:
        return fail("input", f"These are not MusicBrainz recording UUIDs: {malformed}.").to_json()
    # One search for all IDs (rid = recording MBID) instead of one lookup per track.
    query = " OR ".join(f"rid:{m}" for m in recording_mbids)
    status, body, _ = http("GET", f"{MB_API}/recording", params={"query": query, "limit": len(recording_mbids)})
    if status != 200:
        return fail(classify_status(status), f"MusicBrainz verification failed (HTTP {status}).").to_json()
    found = {r["id"]: r for r in body.get("recordings", [])}
    # The search index misses merged MBIDs and very new edits; a direct lookup is authoritative.
    for m in recording_mbids:
        if m in found:
            continue
        status, rec, _ = http("GET", f"{MB_API}/recording/{m}", params={"inc": "artist-credits"})
        if status == 200:
            found[m] = rec                    # rec["id"] may differ from m if MusicBrainz merged it
        elif status != 404:
            return fail(classify_status(status), f"MusicBrainz verification failed (HTTP {status}).").to_json()
    verified = [{
        "recording_mbid": found[m]["id"],
        "title": found[m]["title"],
        "artist": "".join(c["name"] + c.get("joinphrase", "") for c in found[m].get("artist-credit", [])),
        "length_s": (found[m].get("length") or 0) // 1000,
    } for m in recording_mbids if m in found]
    not_found = [m for m in recording_mbids if m not in found]
    if not verified:
        return fail("resource", f"None of these MBIDs exist in MusicBrainz: {not_found}. "
                                "Do not write them; find tracks with search_recordings or lb_radio.").to_json()
    VERIFIED_MBIDS.update(v["recording_mbid"] for v in verified)
    return ok({"verified": verified, "not_found": not_found}).to_json()


def get_fresh_releases(days: int = 30, limit: int = 20) -> str:
    if not 1 <= days <= 90:
        return fail("input", f"days must be between 1 and 90; got {days}.").to_json()
    if not 1 <= limit <= 50:
        return fail("input", f"limit must be between 1 and 50; got {limit}.").to_json()
    status, body, _ = http("GET", f"{LB_API}/user/{LB_USER}/fresh_releases", params={"days": days})
    if status != 200:
        return fail(classify_status(status), f"ListenBrainz fresh releases request failed (HTTP {status}).").to_json()
    releases = sorted(body["payload"]["releases"], key=lambda r: r["release_date"], reverse=True)
    trimmed = [{
        "release_mbid": r["release_mbid"],
        "title": r["release_name"],
        "artist": r["artist_credit_name"],
        "release_date": r["release_date"],
        "type": r.get("release_group_primary_type"),
    } for r in releases[:limit]]
    if not trimmed:
        return fail("resource", f"No fresh releases from the user's artists in the last {days} days.").to_json()
    return ok({"days": days, "total": len(releases), "releases": trimmed}).to_json()


def lb_radio(prompt: str, mode: str = "easy", limit: int = 25) -> str:
    if not prompt.strip():
        return fail("input", "prompt must not be empty, e.g. 'artist:(Khruangbin)' or 'tag:(ambient)'.").to_json()
    if mode not in RADIO_MODES:
        return fail("input", f"mode must be one of {list(RADIO_MODES)}; got '{mode}'.").to_json()
    if not 1 <= limit <= 50:
        return fail("input", f"limit must be between 1 and 50; got {limit}.").to_json()
    # LB Radio builds a playlist server-side and often takes several seconds: measured-slow read override.
    status, body, _ = http("GET", f"{LB_API}/explore/lb-radio", params={"prompt": prompt, "mode": mode},
                           auth=True, timeout=SLOW_READ_TIMEOUT_S)
    if status != 200:
        return fail(classify_status(status), f"LB Radio failed for prompt '{prompt}' (HTTP {status}). "
                                             "Check the prompt syntax, e.g. 'artist:(Name)' or 'tag:(rock)'.").to_json()
    tracks = []
    for t in body["payload"]["jspf"]["playlist"].get("track", [])[:limit]:
        tracks.append({
            "recording_mbid": _mbid_from_identifier(t["identifier"]),
            "title": t.get("title"),
            "artist": t.get("creator"),
            "length_s": (t.get("duration") or 0) // 1000,
        })
    notes = body["payload"].get("feedback", [])                       # radio explains itself here
    if not tracks:
        return fail("resource", f"LB Radio found no tracks for '{prompt}'. {' '.join(notes)}").to_json()
    return ok({"prompt": prompt, "mode": mode, "tracks": tracks, "notes": notes}).to_json()

# ---------------------------------------------------------------- library (playlists)

ENCORE_MARKER = "[Encore]"            # every playlist Encore creates starts with this
JSPF_EXT = "https://musicbrainz.org/doc/jspf#playlist"
EXPORT_SERVICES = ("spotify", "apple_music")
POLICY_REFUSAL = "Policy refusal:"     # error prefix the loop turns into a policy_halt


def _mbid_from_identifier(identifier) -> str:
    """JSPF identifiers are URLs (sometimes a list of them) ending in the MBID."""
    url = identifier[0] if isinstance(identifier, list) else identifier
    return url.rstrip("/").rsplit("/", 1)[-1]


def _own_playlists():
    """The user's playlists (private ones included). Returns (status, list or None)."""
    status, body, _ = http("GET", f"{LB_API}/user/{LB_USER}/playlists", params={"count": 100},
                           auth=True, timeout=SLOW_READ_TIMEOUT_S)
    if status != 200:
        return status, None
    return status, [{
        "playlist_mbid": _mbid_from_identifier(item["playlist"]["identifier"]),
        "title": item["playlist"]["title"],
        "created_by_encore": item["playlist"]["title"].startswith(ENCORE_MARKER),
        "public": item["playlist"].get("extension", {}).get(JSPF_EXT, {}).get("public"),
    } for item in body["playlists"]]


def _unverified(recording_mbids: list[str]) -> list[str]:
    return [m for m in recording_mbids if m not in VERIFIED_MBIDS]


def find_playlists(query: str = "") -> str:
    status, playlists = _own_playlists()
    if playlists is None:
        return fail(classify_status(status), f"ListenBrainz playlists request failed (HTTP {status}).").to_json()
    matches = [p for p in playlists if query.lower() in p["title"].lower()]
    if not matches:
        return fail("resource", f"No playlists match '{query}'." if query else "The user has no playlists.").to_json()
    return ok({"playlists": matches}).to_json()


def create_playlist(title: str, recording_mbids: list[str], public: bool = False) -> str:
    if not title.strip():
        return fail("input", "title must not be empty.").to_json()
    if not recording_mbids:
        return fail("input", "recording_mbids must contain at least one MBID.").to_json()
    unverified = _unverified(recording_mbids)
    if unverified:
        return fail("input", f"Not verified this session: {unverified}. Call verify_recordings first.").to_json()
    if not title.startswith(ENCORE_MARKER):
        title = f"{ENCORE_MARKER} {title.strip()}"
    # Creating is not idempotent, so check for an existing playlist first: a retry must not duplicate it.
    status, playlists = _own_playlists()
    if playlists is None:
        return fail(classify_status(status), f"ListenBrainz playlists request failed (HTTP {status}).").to_json()
    existing = next((p for p in playlists if p["title"] == title), None)
    if existing:
        return fail("resource", f"A playlist titled '{title}' already exists ({existing['playlist_mbid']}). "
                                "Use add_playlist_items to update it instead of creating another.").to_json()
    playlist = {"title": title,
                "track": [{"identifier": f"https://musicbrainz.org/recording/{m}"} for m in recording_mbids],
                "extension": {JSPF_EXT: {"public": public}}}
    status, body, _ = http("POST", f"{LB_API}/playlist/create", body={"playlist": playlist},
                           auth=True, timeout=WRITE_TIMEOUT_S)
    if status != 200:
        return fail(classify_status(status), f"ListenBrainz playlist create failed (HTTP {status}).").to_json()
    return ok({"playlist_mbid": body["playlist_mbid"], "title": title, "track_count": len(recording_mbids)}).to_json()


def add_playlist_items(playlist_mbid: str, recording_mbids: list[str]) -> str:
    if not UUID_RE.match(playlist_mbid or ""):
        return fail("input", f"playlist_mbid must be a playlist UUID; got '{playlist_mbid}'. "
                             "Call find_playlists to get it.").to_json()
    if not recording_mbids:
        return fail("input", "recording_mbids must contain at least one MBID.").to_json()
    unverified = _unverified(recording_mbids)
    if unverified:
        return fail("input", f"Not verified this session: {unverified}. Call verify_recordings first.").to_json()
    tracks = [{"identifier": f"https://musicbrainz.org/recording/{m}"} for m in recording_mbids]
    status, _, _ = http("POST", f"{LB_API}/playlist/{playlist_mbid}/item/add", body={"playlist": {"track": tracks}},
                           auth=True, timeout=WRITE_TIMEOUT_S)
    if status != 200:
        return fail(classify_status(status), f"Adding to playlist {playlist_mbid} failed (HTTP {status}).").to_json()
    return ok({"playlist_mbid": playlist_mbid, "added": recording_mbids}).to_json()


def remove_playlist_items(playlist_mbid: str, recording_mbid: str) -> str:
    if not UUID_RE.match(playlist_mbid or ""):
        return fail("input", f"playlist_mbid must be a playlist UUID; got '{playlist_mbid}'.").to_json()
    if not UUID_RE.match(recording_mbid or ""):
        return fail("input", f"recording_mbid must be a recording UUID; got '{recording_mbid}'.").to_json()
    # The API removes by position, so read the playlist to find where the recording is.
    status, body, _ = http("GET", f"{LB_API}/playlist/{playlist_mbid}", params={"fetch_metadata": "false"},
                           auth=True, timeout=SLOW_READ_TIMEOUT_S)
    if status != 200:
        return fail(classify_status(status), f"Reading playlist {playlist_mbid} failed (HTTP {status}).").to_json()
    positions = [i for i, t in enumerate(body["playlist"]["track"])
                 if _mbid_from_identifier(t["identifier"]) == recording_mbid]
    if not positions:
        return fail("resource", f"Recording {recording_mbid} is not in playlist {playlist_mbid}.").to_json()
    for index in reversed(positions):            # back to front, so earlier positions don't shift
        status, _, _ = http("POST", f"{LB_API}/playlist/{playlist_mbid}/item/delete",
                            body={"index": index, "count": 1}, auth=True, timeout=WRITE_TIMEOUT_S)
        if status != 200:
            return fail(classify_status(status), f"Removing from playlist {playlist_mbid} failed (HTTP {status}).").to_json()
    return ok({"playlist_mbid": playlist_mbid, "removed": recording_mbid, "occurrences": len(positions)}).to_json()


def delete_playlist(playlist_mbid: str) -> str:
    if not UUID_RE.match(playlist_mbid or ""):
        return fail("input", f"playlist_mbid must be a playlist UUID; got '{playlist_mbid}'. "
                             "Call find_playlists to get it.").to_json()
    status, playlists = _own_playlists()
    if playlists is None:
        return fail(classify_status(status), f"ListenBrainz playlists request failed (HTTP {status}).").to_json()
    target = next((p for p in playlists if p["playlist_mbid"] == playlist_mbid), None)
    if target is None:
        return fail("resource", f"The user has no playlist {playlist_mbid}.").to_json()
    if not target["created_by_encore"]:               # blast radius: never touch the user's own playlists
        return fail("resource", f"{POLICY_REFUSAL} '{target['title']}' was not created by Encore, "
                                "so Encore will not delete it.").to_json()
    status, _, _ = http("POST", f"{LB_API}/playlist/{playlist_mbid}/delete", auth=True, timeout=WRITE_TIMEOUT_S)
    if status != 200:
        return fail(classify_status(status), f"Deleting playlist {playlist_mbid} failed (HTTP {status}).").to_json()
    return ok({"deleted": playlist_mbid, "title": target["title"]}).to_json()


def export_playlist(playlist_mbid: str, service: str) -> str:
    if not UUID_RE.match(playlist_mbid or ""):
        return fail("input", f"playlist_mbid must be a playlist UUID; got '{playlist_mbid}'.").to_json()
    if service not in EXPORT_SERVICES:
        return fail("input", f"service must be one of {list(EXPORT_SERVICES)}; got '{service}'.").to_json()
    status, body, _ = http("POST", f"{LB_API}/playlist/{playlist_mbid}/export/{service}",
                           auth=True, timeout=WRITE_TIMEOUT_S)
    if status in (400, 401, 403):
        # Inputs were validated above, so a refusal here means the service isn't connected.
        detail = body.get("error", "") if isinstance(body, dict) else ""
        return fail("fatal", f"Export to {service} was refused (HTTP {status}): {detail} Connect {service} "
                             "with playlist permission in ListenBrainz settings, then try again.").to_json()
    if status != 200:
        return fail(classify_status(status), f"Export to {service} failed (HTTP {status}).").to_json()
    return ok({"playlist_mbid": playlist_mbid, "service": service,
               "external_url": body.get("external_url") if isinstance(body, dict) else None}).to_json()


# ---------------------------------------------------------------- memory

# Preferences the user states this session. TODO: move into hot state (Part 5.1).
SESSION_PREFERENCES: list[str] = []


def note_preference(preference: str) -> str:
    if not preference.strip():
        return fail("input", "preference must not be empty.").to_json()
    SESSION_PREFERENCES.append(preference.strip())
    return ok({"noted": preference.strip(), "session_preferences": SESSION_PREFERENCES}).to_json()


def search_past_sessions(query: str) -> str:
    # TODO (Part 5): query the episodic ChromaDB collection, filtered by ENCORE_USER_ID.
    return fail("resource", "Episodic memory is not available yet; ask the user instead.").to_json()


def search_music_knowledge(query: str) -> str:
    # TODO (Part 5): query the semantic ChromaDB collection and return top chunks with sources.
    return fail("resource", "The music knowledge base is not available yet.").to_json()


# ---------------------------------------------------------------- control

FINAL_STATUSES = ("answered", "answered_low_confidence", "stuck", "budget_exceeded", "policy_halt")
CONFIDENCE_LEVELS = ("high", "medium", "low")


def final_answer(status: str, answer: str, confidence: str, sources: Optional[list[str]] = None) -> str:
    """Not an API call: validates the model's closing claim. The loop decides the real status."""
    if status not in FINAL_STATUSES:
        return fail("input", f"status must be one of {list(FINAL_STATUSES)}; got '{status}'.").to_json()
    if confidence not in CONFIDENCE_LEVELS:
        return fail("input", f"confidence must be one of {list(CONFIDENCE_LEVELS)}; got '{confidence}'.").to_json()
    if not answer.strip():
        return fail("input", "answer must not be empty.").to_json()
    return ok({"status": status, "answer": answer, "confidence": confidence, "sources": sources or []}).to_json()


# TODO 1: implement the remaining required tools in Part 3 (same ToolResult contract)
# TODO 2: write a JSON schema for every tool: descriptions say when NOT to use it,
#         bounded values are enums, write tools state their side effects (Part 3)

# IMPORT TOOL SCHEMA FROM schemas.py
TOOLS = {
    "get_recent_listens": get_recent_listens,
    "search_recordings": search_recordings,
    "get_feedback": get_feedback,
    "lookup_artist": lookup_artist,
    "get_top_recordings_for_artist": get_top_recordings_for_artist,
    "verify_recordings": verify_recordings,
    "get_fresh_releases": get_fresh_releases,
    "lb_radio": lb_radio,
    "find_playlists": find_playlists,
    "add_playlist_items": add_playlist_items, 
    "set_feedback": set_feedback,
    "delete_playlist": delete_playlist,
    "search_past_sessions": search_past_sessions,
    "create_playlist": create_playlist,
    "remove_playlist_items": remove_playlist_items,
    "export_playlist": export_playlist,
    "search_music_knowledge": search_music_knowledge,
    "note_preference": note_preference,
    "final_answer": final_answer,
}

def build_windowed_context(all_steps, rolling_summary): 
    step_starts = []
    for i, message in enumerate(all_steps):
        if message["role"] == "assistant":
            step_starts.append(i)
    if len(step_starts) <= WINDOW_SIZE:
        return [{"role": "system", "content": SYSTEM_PROMPT}] + all_steps

    cutoff = step_starts[-WINDOW_SIZE]
    steps_to_summarize, steps_to_keep = all_steps[:cutoff], all_steps[cutoff:]

    print(
            f"WINDOWING: summarizing {len(step_starts) - WINDOW_SIZE} "
            f"older steps; keeping {WINDOW_SIZE} recent steps."
        )

    summary_lines = []
    calls_by_id = {}

    for message in steps_to_summarize:
        if message["role"] == "user":
            summary_lines.append(
                f"User request: {message['content']}"
            )

        elif message["role"] == "assistant":
            for call in message.get("tool_calls") or []:
                calls_by_id[call["id"]] = call["function"]

        elif message["role"] == "tool":
            call = calls_by_id[message["tool_call_id"]]
            tool_name = call["name"]
            arguments = call["arguments"]
            result = message["content"]

            if tool_name == "search_web":
                search_data = json.loads(result)

                # Successful searches return a list.
                # Error dictionaries stay intact.
                if isinstance(search_data, list):
                    result = json.dumps([
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", "")
                        }
                        for item in search_data
                    ])

            summary_lines.append(
                f"{tool_name}({arguments}) -> {result}"
            )

    rolling_summary["content"] = ("Earlier observations:\n" + "\n".join(summary_lines))

    print("\nROLLING SUMMARY:")
    print(rolling_summary["content"])
    print(f"Summary length: {len(rolling_summary['content'])} characters")

    return [{"role": "system", "content": SYSTEM_PROMPT}, rolling_summary] + steps_to_keep



def log_tool_call(step, tool_name, arguments, result, latency_ms, log_path="agent_trace.jsonl"):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "tool_name": tool_name,
        "arguments": arguments,
        "result": result,
        "latency_ms": latency_ms
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def backoff_delays(attempts: int = 4, base: float = 1.0, cap: float = 30.0):
    """Exponential backoff with full jitter. The LOOP retries transient errors, never the model."""
    return [random.uniform(0, min(cap, base * 2 ** i)) for i in range(attempts)]


SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system_v1.md"
FINAL_ANSWER_SCHEMA = router.tools_for(["none"])[0]           # tools_for always includes final_answer
FORCE_FINAL_ANSWER = {"type": "function", "function": {"name": "final_answer"}}
BUDGET_NOTE = ("You have run out of steps. Call final_answer now: say what you accomplished, "
               "what is left undone, and why.")


def call_tool(name: str, arguments_json: str, allowed: set[str]) -> str:
    """Run one tool the model asked for. Every mistake becomes an observation, never a crash."""
    if name not in allowed:
        return fail("input", f"Tool '{name}' is not available for this request. "
                             f"Use one of: {sorted(allowed)}.").to_json()
    try:
        arguments = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return fail("input", f"Arguments for {name} were not valid JSON: {arguments_json!r}").to_json()
    try:
        return TOOLS[name](**arguments)
    except TypeError as exc:                     # missing, extra, or misnamed arguments
        return fail("input", f"Bad arguments for {name}: {exc}").to_json()
    except Exception as exc:                     # a bug or an API shape we didn't expect
        return fail("resource", f"{name} failed unexpectedly ({type(exc).__name__}). Try another approach.").to_json()


NO_AUTO_RETRY = {"add_playlist_items", "export_playlist"}   # not idempotent: a retry could apply them twice


def call_tool_with_retry(name: str, arguments_json: str, allowed: set[str]) -> str:
    """The LOOP retries transient errors with backoff; the model only sees the final outcome."""
    result = call_tool(name, arguments_json, allowed)
    error = json.loads(result)
    if error["error_category"] != "transient":
        return result
    if name in NO_AUTO_RETRY:
        return fail("resource", f"{error['error']} This write may or may not have been applied, so it was not "
                                "retried. Check the playlist before trying again.").to_json()
    for attempt, delay in enumerate(backoff_delays(), start=2):
        print(f"    {name}: {error['error']} Retrying in {delay:.1f}s (attempt {attempt}).")
        time.sleep(delay)
        result = call_tool(name, arguments_json, allowed)
        error = json.loads(result)
        if error["error_category"] != "transient":
            return result
    # Still failing after backoff: the spec treats this as a block, so stop instead of hammering the service.
    return fail("fatal", f"{error['error']} Still failing after retries; the service may be refusing "
                         "requests. Try again later.").to_json()


def finish(messages: list[dict], mode: str, note: Optional[str] = None) -> tuple[str, str]:
    """Every normal exit comes through here: the model writes final_answer, the loop decides the status."""
    if note:
        messages = messages + [{"role": "system", "content": note}]
    claim = None
    for tier in ("expensive", "cheap"):          # if the expensive model fails, don't lose the answer
        try:
            message, _ = llm.chat(messages, mode, tier, [FINAL_ANSWER_SCHEMA], FORCE_FINAL_ANSWER)
        except requests.RequestException:
            continue
        if message.get("tool_calls"):            # the structured answer we asked for
            try:
                arguments = json.loads(message["tool_calls"][0]["function"]["arguments"])
                result = json.loads(final_answer(**arguments))
            except (TypeError, json.JSONDecodeError):
                continue
            if result["success"]:
                claim = result["data"]
                break
        elif (message.get("content") or "").strip():
            # Some models ignore the forced tool_choice and just reply. Keep the answer; we have no
            # confidence claim from the model, so record it as medium.
            claim = {"status": "answered", "answer": message["content"].strip(), "confidence": "medium", "sources": []}
            break
    if claim is None:
        return "stuck", "I couldn't put together a final answer this time. Please try again."
    # The loop, not the model, has the last word on status.
    if note == BUDGET_NOTE:
        status = "budget_exceeded"
    elif claim["status"] == "answered" and claim["confidence"] == "low":
        status = "answered_low_confidence"
    else:
        status = claim["status"]
    return status, claim["answer"]


def prompt_section(text: str, heading: str) -> str:
    """Return one '# Heading' section of the system prompt, heading line included.

    Collects every line from '# heading' up to (not including) the next '# ' heading.
    """
    section_lines = []
    inside_section = False

    for line in text.splitlines():
        if line.strip() == f"# {heading}":
            # Found the heading we want: start collecting.
            inside_section = True
            section_lines.append(line)
        elif line.startswith("# ") and inside_section:
            # Reached the next heading: the section is over.
            break
        elif inside_section:
            section_lines.append(line)

    if not section_lines:
        # Fail loudly: a missing Rules section would silently turn off constraint reinjection.
        raise ValueError(f"The system prompt has no '# {heading}' section.")

    return "\n".join(section_lines).strip()


def build_messages(rules: str, guidance: str, request: str, history: list[dict]) -> list[dict]:
    """The messages for one model call, in the front-loaded order from Part 5.1.

    The rules are rebuilt here on every call and never stored in history,
    so nothing in the conversation can push them out or summarize them away.
    """
    messages = []

    # 1. Reinjected constraints first.
    messages.append({"role": "system", "content": rules})

    # 2. Role, memory, and tool guidance.
    messages.append({"role": "system", "content": guidance})

    # 3. The current objective, restated so it stays visible after many tool steps.
    messages.append({"role": "system", "content": f"Current request: {request}"})

    # 4. (later) Hot state and key facts about the user.
    # 5. (later) Retrieved past-session summaries.

    # 6. The conversation so far.
    messages.extend(history)

    return messages


def run_request(request: str, history: list[dict], rules: str, guidance: str, mode: str) -> tuple[str, str]:
    """One user request through the bounded ReAct loop. Appends this turn to history."""
    route = router.route(request, mode)
    schemas = router.tools_for(route["domains"])
    allowed = {s["function"]["name"] for s in schemas} - {"final_answer"}
    history.append({"role": "user", "content": request})

    for step in range(1, MAX_STEPS + 1):
        messages = build_messages(rules, guidance, request, history)
        message, _ = llm.chat(messages, mode, "cheap", schemas)
        tool_calls = message.get("tool_calls") or []

        # Exit: the model thinks it's done (text only, or it called final_answer).
        if not tool_calls or any(c["function"]["name"] == "final_answer" for c in tool_calls):
            status, answer = finish(messages, mode)
            break

        # Act: run each requested tool and feed the result back as an observation.
        history.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": tool_calls})
        halt = None # halt carries info from inner to outer loop about reason for halting after fatal error or policy failure
        for call in tool_calls:
            name = call["function"]["name"]
            result = call_tool_with_retry(name, call["function"]["arguments"], allowed)
            parsed = json.loads(result)
            print(f"  [{step}] {name}: {'ok' if parsed['success'] else parsed['error']}")
            if name == "search_recordings" and parsed["success"]:          # search results count as verified
                VERIFIED_MBIDS.update(r["recording_mbid"] for r in parsed["data"]["recordings"])
            history.append({"role": "tool", "tool_call_id": call["id"], "content": result})

            # Exits the loop decides on its own, without asking the model.
            if parsed["error_category"] == "fatal":
                halt = ("stuck", f"I had to stop: {parsed['error']}")
            elif (parsed["error"] or "").startswith(POLICY_REFUSAL):
                halt = ("policy_halt", f"I can't do that. {parsed['error'][len(POLICY_REFUSAL):].strip()}")
            if halt:
                break
        if halt:
            status, answer = halt
            break
    else:
        # Exit: out of steps without finishing.
        messages = build_messages(rules, guidance, request, history)
        status, answer = finish(messages, mode, note=BUDGET_NOTE)

    history.append({"role": "assistant", "content": answer})
    return status, answer


def describe_crash(exc: Exception) -> str:
    """A message the user can act on, for an exception that escaped run_request."""
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status == 429:
        return "The language model is rate-limited (or today's free-tier limit is used up). Try again later."
    if status in (401, 402, 403):
        return f"The language model refused the request (HTTP {status}). Check your OpenRouter key and credits."
    if isinstance(exc, requests.RequestException):
        return f"I couldn't reach the language model ({type(exc).__name__}). Check your connection and try again."
    return f"Something went wrong on my side ({type(exc).__name__}: {exc}). Please try again."


def run_session(mode: str) -> None:
    # TODO 3: session start -- load procedural memory (prompts/system_v1.md) and hot state,
    #         retrieve episodic memories for the first message, and front-load them (Part 5)
    # TODO 4: bounded ReAct loop -- route tools (Lab 4), reinject constraints every call
    #         (Lab 3), retry transient errors with backoff_delays(), gate writes behind
    #         approval, compress working memory past its budget, log every step (Part 6)
    # TODO 5: end the loop only through final_answer or a termination status (Part 4)
    # TODO 6: session end -- structured summary, quality check, dedup, store (Part 5)
    # Procedural memory: read the prompt once and split it into the reinjected rules and the rest.
    prompt_text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    rules = prompt_section(prompt_text, "Rules")
    guidance = "\n\n".join([
        prompt_section(prompt_text, "Role"),
        prompt_section(prompt_text, "Memory"),
        prompt_section(prompt_text, "Tools"),
    ])
    history: list[dict] = []                                           # working memory, kept across requests

    print("Encore is ready. Ask about your music, or type 'quit' to end the session.")
    while True:
        request = input("\nyou> ").strip()
        if request.lower() in ("quit", "exit", "q"):
            break
        if not request:
            continue
        turn_start = len(history)
        try:
            status, answer = run_request(request, history, rules, guidance, mode)
        except Exception as exc:
            # One bad request must not end the session. Roll back this turn's half-written messages
            # (e.g. a tool call with no result) so the next request starts from a valid history.
            del history[turn_start:]
            status, answer = "stuck", describe_crash(exc)
        print(f"\nencore [{status}]> {answer}")


def forget_user(user_id: str) -> None:
    # TODO 7: delete every stored item for user_id from EVERY store and print the counts
    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encore, a ListenBrainz music agent that remembers.")
    parser.add_argument("mode", choices=["online", "offline"])
    parser.add_argument("--forget", action="store_true", help="delete every memory for ENCORE_USER_ID")
    parser.add_argument("--inject", metavar="FILE.json", help="fault injection: transient_rate, max_steps, seed")
    args = parser.parse_args()
    if args.inject:
        load_injection(args.inject)
    if args.forget:
        forget_user(ENCORE_USER_ID)
    else:
        run_session(args.mode)
