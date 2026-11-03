"""Unit layer: the router's tool masking (Part 3). No model call is made."""

import router


def tool_names(domains):
    return {schema["function"]["name"] for schema in router.tools_for(domains)}


def test_discovery_brings_the_verification_tools():
    # Found songs must be verified before use, and verification lives in catalog.
    names = tool_names(["discovery"])
    assert "lb_radio" in names
    assert "verify_recordings" in names and "search_recordings" in names


def test_library_brings_the_verification_tools():
    names = tool_names(["library"])
    assert "add_playlist_items" in names and "verify_recordings" in names


def test_catalog_alone_does_not_bring_write_tools():
    # Companions only add the tools a domain depends on, never write tools it didn't ask for.
    names = tool_names(["catalog"])
    assert "create_playlist" not in names and "lb_radio" not in names


def test_final_answer_is_always_offered():
    assert "final_answer" in tool_names(["none"])
