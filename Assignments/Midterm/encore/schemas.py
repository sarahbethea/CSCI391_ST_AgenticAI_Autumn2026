"""
JSON schemas for every Encore tool (Part 3). encore.py imports TOOL_SCHEMAS; this file imports nothing
from encore.py, so the dependency only goes one way.

Each description says what the tool does, what to pass, when to prefer it, and when not to use it.
Bounded values are enums. Write tools state their side effects and whether they are idempotent.
"""

MBID = {"type": "string", "description": "A MusicBrainz UUID, e.g. 'f5971e52-c1aa-44aa-aabc-93e4831380ed'."}
MBID_LIST = {"type": "array", "items": {"type": "string"}, "minItems": 1}


def _tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


TOOL_SCHEMAS = [
    # ------------------------------------------------------------ listening (read)
    _tool(
        "get_recent_listens",
        "Get the songs the user listened to most recently, newest first, with artist, track, timestamp, and "
        "recording_mbid. Use it for 'what have I been playing lately?' and to find tracks to leave out of a "
        "playlist ('nothing I've heard this week'). "
        "Do not use this to find the user's favorites; use get_feedback for loved songs.",
        {"count": {"type": "integer", "minimum": 1, "maximum": 100,
                   "description": "How many recent listens to return. Default 25."}},
        [],
    ),
    _tool(
        "get_feedback",
        "Get recordings the user has marked as loved or hated on ListenBrainz, with track, artist, "
        "recording_mbid, and artist_mbids. Use loved songs as seeds for recommendations and hated songs as "
        "exclusions. "
        "Do not use this to love or hate a song; use set_feedback.",
        {"kind": {"type": "string", "enum": ["loved", "hated"],
                  "description": "Which feedback to return. Default 'loved'."},
         "count": {"type": "integer", "minimum": 1, "maximum": 100,
                   "description": "How many recordings to return. Default 25."}},
        [],
    ),

    # ------------------------------------------------------------ catalog (read)
    _tool(
        "search_recordings",
        "Search MusicBrainz for a song by title (and optionally artist). Returns recording_mbid, title, artist, "
        "length, and first release date. Use it when the user names a specific song and you need its MBID. "
        "Recordings found here count as verified. "
        "Do not use this to discover new music; use lb_radio or get_top_recordings_for_artist.",
        {"title": {"type": "string", "description": "The song title."},
         "artist": {"type": "string", "description": "The artist name, to narrow the search. Optional."},
         "limit": {"type": "integer", "minimum": 1, "maximum": 25, "description": "Max results. Default 5."}},
        ["title"],
    ),
    _tool(
        "lookup_artist",
        "Look up an artist on MusicBrainz with their relationships: band members (with instruments and years), "
        "the bands a person belongs to, and collaborations. Pass artist_mbid if you have one, otherwise name. "
        "Use it for 'who's in that band?' or 'what else has this drummer played on?'. "
        "Do not use this to get an artist's songs; use get_top_recordings_for_artist.",
        {"artist_mbid": {**MBID, "description": "The artist's MusicBrainz UUID, if known. Preferred over name."},
         "name": {"type": "string", "description": "The artist name, used only when artist_mbid is unknown."}},
        [],
    ),
    _tool(
        "get_top_recordings_for_artist",
        "Get an artist's most-listened recordings across all ListenBrainz users, most popular first, with "
        "recording_mbid, title, length, and listen count. Use it to build playlists 'from artists I love'. "
        "If you only have the artist's name, call lookup_artist first to get the artist_mbid. "
        "Do not use this for the user's own listening; use get_recent_listens or get_feedback.",
        {"artist_mbid": {**MBID, "description": "The artist's MusicBrainz UUID."},
         "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Max recordings. Default 10."}},
        ["artist_mbid"],
    ),
    _tool(
        "verify_recordings",
        "Confirm that recording MBIDs exist in MusicBrainz, returning title, artist, and length for each real "
        "one and a not_found list for the rest. REQUIRED before create_playlist or add_playlist_items: those "
        "tools refuse any MBID not verified (or found by search_recordings) in this session. "
        "Do not use this to search for songs by name; use search_recordings.",
        {"recording_mbids": {**MBID_LIST, "maxItems": 25,
                             "description": "1 to 25 recording MBIDs taken from earlier tool results."}},
        ["recording_mbids"],
    ),

    # ------------------------------------------------------------ discovery (read)
    _tool(
        "get_fresh_releases",
        "Get new albums and singles from artists the user listens to, newest first, with release title, "
        "artist, date, and type. Use it for 'any new releases from artists I like?'. "
        "Do not use this to find individual songs for a playlist; use lb_radio.",
        {"days": {"type": "integer", "minimum": 1, "maximum": 90, "description": "How far back to look. Default 30."},
         "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Max releases. Default 20."}},
        [],
    ),
    _tool(
        "lb_radio",
        "Generate candidate tracks with ListenBrainz Radio from a prompt, returning recording_mbid, title, "
        "artist, and length. Prompt syntax: 'artist:(Khruangbin)', 'tag:(ambient)', 'tag:(rock, 80s)', or "
        "'stats:(username)' for tracks like the user's own listening. Use it to find new music for a playlist. "
        "Results are candidates: verify them before writing. "
        "Do not use this to look up a specific song; use search_recordings.",
        {"prompt": {"type": "string", "description": "An LB Radio prompt, e.g. 'tag:(ambient)'."},
         "mode": {"type": "string", "enum": ["easy", "medium", "hard"],
                  "description": "easy = familiar, close matches; hard = more adventurous. Default 'easy'."},
         "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Max tracks. Default 25."}},
        ["prompt"],
    ),

    # ------------------------------------------------------------ library (writes, plus one read)
    _tool(
        "find_playlists",
        "List the user's own ListenBrainz playlists (private ones included) with playlist_mbid, title, and "
        "created_by_encore. Read-only. Call it before create_playlist to avoid duplicates, and to get a "
        "playlist_mbid for any other playlist tool. "
        "Do not use this to see a playlist's tracks; it returns titles only.",
        {"query": {"type": "string", "description": "Text the title must contain. Empty lists every playlist."}},
        [],
    ),
    _tool(
        "create_playlist",
        "WRITE: create a new playlist in the user's ListenBrainz account. Side effect: a new playlist appears "
        "in their account; '[Encore]' is added to the title. NOT idempotent, so it refuses a title that already "
        "exists and you should use add_playlist_items for that playlist instead. Every MBID must be verified "
        "this session; if not, call verify_recordings first. "
        "Do not use this to add songs to an existing playlist; use add_playlist_items.",
        {"title": {"type": "string", "description": "Playlist title, e.g. 'Focus — Oct 28'."},
         "recording_mbids": {**MBID_LIST, "description": "Verified recording MBIDs, in play order."},
         "public": {"type": "boolean", "description": "Whether others can see it. Default false (private)."}},
        ["title", "recording_mbids"],
    ),
    _tool(
        "add_playlist_items",
        "WRITE: append recordings to the end of an existing playlist. Side effect: the playlist changes. NOT "
        "idempotent: calling twice adds the songs twice. Every MBID must be verified this session; if not, call "
        "verify_recordings first. If you don't have the playlist_mbid, call find_playlists first. "
        "Do not use this to make a new playlist; use create_playlist.",
        {"playlist_mbid": {**MBID, "description": "The playlist's UUID from find_playlists or create_playlist."},
         "recording_mbids": {**MBID_LIST, "description": "Verified recording MBIDs to append."}},
        ["playlist_mbid", "recording_mbids"],
    ),
    _tool(
        "remove_playlist_items",
        "WRITE: remove every occurrence of one recording from a playlist. Side effect: the playlist changes. "
        "Idempotent in effect: once removed, a second call returns a not-found error and changes nothing. "
        "Do not use this to delete a whole playlist; use delete_playlist.",
        {"playlist_mbid": {**MBID, "description": "The playlist's UUID from find_playlists."},
         "recording_mbid": {**MBID, "description": "The recording to remove."}},
        ["playlist_mbid", "recording_mbid"],
    ),
    _tool(
        "set_feedback",
        "WRITE: love, hate, or clear the user's feedback on one recording. Side effect: changes the user's "
        "ListenBrainz feedback. Idempotent: repeating the same action has no further effect. If you don't have "
        "a recording MBID, call search_recordings first. "
        "Do not use this to read existing feedback; use get_feedback.",
        {"recording_mbid": {**MBID, "description": "The recording to rate."},
         "action": {"type": "string", "enum": ["love", "hate", "clear"],
                    "description": "love, hate, or clear (remove any feedback)."}},
        ["recording_mbid", "action"],
    ),
    _tool(
        "export_playlist",
        "WRITE: copy a ListenBrainz playlist into the user's Spotify or Apple Music library. Side effect: a new "
        "playlist appears in that streaming service, which Encore cannot undo. NOT idempotent: exporting twice "
        "creates two copies. Always requires the user's approval. Fails with a fatal error if the service isn't "
        "connected in ListenBrainz settings. "
        "Do not use this unless the user asked to export.",
        {"playlist_mbid": {**MBID, "description": "The ListenBrainz playlist to export."},
         "service": {"type": "string", "enum": ["spotify", "apple_music"], "description": "Where to export it."}},
        ["playlist_mbid", "service"],
    ),
    _tool(
        "delete_playlist",
        "WRITE: permanently delete one playlist that Encore created (title starts with '[Encore]'). Side effect: "
        "the playlist is gone and cannot be restored. Always requires the user's approval. Refuses any playlist "
        "Encore did not create. For 'delete all my playlists', call find_playlists and delete only those with "
        "created_by_encore = true. "
        "Do not use this to remove a single song; use remove_playlist_items.",
        {"playlist_mbid": {**MBID, "description": "The playlist's UUID from find_playlists."}},
        ["playlist_mbid"],
    ),

    # ------------------------------------------------------------ memory
    _tool(
        "search_past_sessions",
        "Search Encore's memory of past conversations with this user: what was asked, decided, created, "
        "preferred, or left unfinished. Use it when the user refers back ('like last time', 'the playlist from "
        "last week'). Results may be outdated; confirm conflicts with the user. "
        "Do not use this for the user's listening history (use get_recent_listens) or for how ListenBrainz "
        "works (use search_music_knowledge).",
        {"query": {"type": "string", "description": "What to look for, e.g. 'focus playlist'."}},
        ["query"],
    ),
    _tool(
        "search_music_knowledge",
        "Search Encore's knowledge base: ListenBrainz and MusicBrainz documentation and a music glossary of "
        "genres and moods. Returns the top passages with their sources. Use it for how-to questions ('why "
        "aren't my Apple Music listens showing up?') and music terms ('what is shoegaze?'). "
        "Do not use this for anything about this user's past conversations; use search_past_sessions.",
        {"query": {"type": "string", "description": "The question or term to look up."}},
        ["query"],
    ),
    _tool(
        "note_preference",
        "Record a preference the user just stated ('no Christmas music', 'instrumental only for studying') so "
        "Encore follows it for the rest of the session and remembers it afterward. "
        "Do not use this for passing requests that apply to one answer only.",
        {"preference": {"type": "string", "description": "The preference, in a short sentence."}},
        ["preference"],
    ),

    # ------------------------------------------------------------ control
    _tool(
        "final_answer",
        "Finish the request and reply to the user. Call it exactly once, when the goal is met or you cannot "
        "make further progress. "
        "Do not use this while a needed tool call is still pending.",
        {"status": {"type": "string",
                    "enum": ["answered", "answered_low_confidence", "stuck", "budget_exceeded", "policy_halt"],
                    "description": "answered; answered_low_confidence (say what is uncertain); stuck (say what "
                                   "was done and why you stopped); policy_halt (the request was forbidden)."},
         "answer": {"type": "string", "description": "The reply shown to the user."},
         "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
         "sources": {"type": "array", "items": {"type": "string"},
                     "description": "MBIDs, playlist IDs, or knowledge-base sources the answer relied on."}},
        ["status", "answer", "confidence", "sources"],
    ),
]
