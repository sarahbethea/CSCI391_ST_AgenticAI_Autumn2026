import json

import jsonschema
import requests

import llm
from schemas import TOOL_SCHEMAS

TOOLSETS = {
    "listening": ["get_recent_listens", "get_feedback"],
    "catalog": ["search_recordings", "lookup_artist", "get_top_recordings_for_artist", "verify_recordings"],
    "discovery": ["get_fresh_releases", "lb_radio"],
    "library": ["find_playlists", "create_playlist", "add_playlist_items", "remove_playlist_items",
                "set_feedback", "export_playlist", "delete_playlist"],
    "memory": ["search_past_sessions", "search_music_knowledge", "note_preference"],
    "none": [],
}
DOMAINS = list(TOOLSETS)

ROUTER_PROMPT = """
You are a request router for Encore, a music agent. Call classify_intent with every
tool domain the user's request needs. Most requests need more than one.

- listening: the user's own recent listens, loved or hated songs
- catalog: looking up songs or artists, band members, an artist's popular songs, verifying tracks
- discovery: finding new music (radio, recommendations), new releases
- library: the user's playlists (find, create, edit, delete, export) and loving/hating a song
- memory: references to past sessions ("last time"), how ListenBrainz works, music terms,
  or the user stating a preference
- none: small talk that needs no tools

Building a playlist usually needs discovery + catalog + library.
Do not answer the request. Only classify it.
"""

CLASSIFIER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "classify_intent",
        "description": "Report which toolset domains the request needs.",
        "parameters": {
            "type": "object",
            "properties": {
                "domains": {
                    "type": "array",
                    "items": {"type": "string", "enum": DOMAINS},
                    "description": "Every toolset domain the request needs."
                }
            },
            "required": ["domains"],
            "additionalProperties": False,
        },
    },
}


FORCE_CLASSIFIER = {"type": "function", "function": {"name": "classify_intent"}}

ALL_DOMAINS = [domain for domain in DOMAINS if domain != "none"]


def route(request, mode):
    """Classify the request into tool domains. Never raises: any failure falls back to every domain."""
    meta = {}                       # stays {} if chat() itself fails
    try:
        message, meta = llm.chat([{"role": "system", "content": ROUTER_PROMPT}, {"role": "user", "content": request}],
                                 mode, "cheap", [CLASSIFIER_SCHEMA], FORCE_CLASSIFIER)

        # extract arguments (contains domains)
        arguments_text = message["tool_calls"][0]["function"]["arguments"]

        # turn into python dict, so arguments will look like {"domains": ["catalog", "library"]}
        arguments = json.loads(arguments_text)

        # validate schema
        jsonschema.validate(instance=arguments, schema=CLASSIFIER_SCHEMA["function"]["parameters"])

        # retrieve domains; "none" only means something on its own
        domains = list(dict.fromkeys(arguments["domains"]))
        if "none" in domains and len(domains) > 1:
            domains.remove("none")

        # If empty list, use every domain
        if not domains:
            return {"domains": ALL_DOMAINS, "fallback": True, "error": "empty domain list", "meta": meta}

    except (requests.RequestException, KeyError, TypeError, IndexError,
            json.JSONDecodeError, jsonschema.ValidationError) as err:
        # any routing failure: offer every domain rather than stop the agent
        return {"domains": ALL_DOMAINS, "fallback": True, "error": f"{type(err).__name__}: {err}"[:200], "meta": meta}

    return {"domains": domains, "fallback": False, "error": None, "meta": meta}


# Domains that can't do their job safely without another domain's tools. Songs found by discovery
# and songs written by library must be verified first, and verification lives in catalog. This is
# enforced here in code, so it doesn't depend on the cheap router remembering a hint in its prompt.

COMPANIONS = {
    "discovery": ["catalog"],
    "library": ["catalog"],
}


def tools_for(domains):
    """The schemas the loop offers the model for these domains. final_answer is always included."""
    names = {"final_answer"}
    for domain in domains:
        names.update(TOOLSETS[domain])

        # Bring along any companion domain this one depends on.
        if domain in COMPANIONS:
            for companion in COMPANIONS[domain]:
                names.update(TOOLSETS[companion])

    return [s for s in TOOL_SCHEMAS if s["function"]["name"] in names]