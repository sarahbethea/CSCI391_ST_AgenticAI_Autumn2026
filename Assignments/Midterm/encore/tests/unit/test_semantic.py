"""Unit layer: semantic memory (Part 5). A word tokenizer and fake embeddings stand in for the model."""

import json

import pytest

import semantic

API_DOC = {
    "name": "lb_users_api_misc.md", "title": "Miscellaneous",
    "url": "https://listenbrainz.readthedocs.io/en/latest/users/api/misc.html",
    "text": "# Miscellaneous\nVarious endpoints.\n\n## Explore API\n\n"
            "### GET /1/explore/lb-radio\nGenerate a playlist with LB Radio.\n"
            "mode – Must be easy, medium or hard.\n\n"
            "### GET /1/explore/color/(color)\nFetch releases whose cover art matches a color.",
}
RATE_DOC = {
    "name": "lb_users_api_index.md", "title": "ListenBrainz API",
    "url": "https://listenbrainz.readthedocs.io/en/latest/users/api/index.html",
    "text": "# ListenBrainz API\n\n## Rate limiting\n"
            "X-RateLimit-Reset-In: Number of seconds when current time window expires.\n"
            "If the client exceeds the limit the server will respond with error code 429: Too Many Requests.",
}


# ---------------------------------------------------------------- chunking

def test_sections_keep_each_endpoint_together():
    chunks = semantic.chunk_sections(API_DOC)
    radio = [chunk for chunk in chunks if "lb-radio" in chunk["text"]]
    assert len(radio) == 1, "one endpoint, one chunk"
    assert "Must be easy, medium or hard" in radio[0]["text"]
    assert radio[0]["section"] == "GET /1/explore/lb-radio"


def test_an_empty_heading_is_carried_into_the_next_chunk():
    radio = [chunk for chunk in semantic.chunk_sections(API_DOC) if "lb-radio" in chunk["text"]][0]
    assert radio["text"].startswith("## Explore API"), "the parent heading gives the endpoint its context"


def test_fixed_windows_overlap_and_respect_the_limit(monkeypatch):
    monkeypatch.setattr(semantic, "FIXED_CHUNK_TOKENS", 12)
    monkeypatch.setattr(semantic, "FIXED_OVERLAP_TOKENS", 4)
    document = {"name": "d.md", "title": "D", "url": "", "text": " ".join(f"w{i}" for i in range(40))}
    chunks = semantic.chunk_fixed(document)
    assert len(chunks) > 1
    for chunk in chunks:
        assert semantic.token_count(chunk["text"]) <= 12
    first_words = chunks[0]["text"].split()
    second_words = chunks[1]["text"].split()
    assert first_words[-4:] == second_words[:4], "consecutive windows share the overlap"


def test_a_long_section_is_split_and_every_piece_keeps_its_heading(monkeypatch):
    monkeypatch.setattr(semantic, "MODEL_TOKEN_LIMIT", 100)
    long_doc = {"name": "l.md", "title": "L", "url": "",
                "text": "## Long section\n" + " ".join(f"word{i}" for i in range(300))}
    chunks = semantic.chunk_sections(long_doc)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk["text"].startswith("## Long section")
        assert semantic.token_count(chunk["text"]) <= 100


def test_a_chunk_over_the_model_limit_refuses_to_build(monkeypatch):
    monkeypatch.setattr(semantic, "CHUNKERS", {"sections": lambda document: [{"text": "x " * 300, "section": ""}]})
    with pytest.raises(ValueError):
        semantic.make_chunks("sections", [API_DOC])


def test_the_empty_glossary_template_is_not_indexed(tmp_path, monkeypatch):
    template = tmp_path / "glossary.md"
    template.write_text("<!-- instructions\n## Term name\nexample -->\n\n# Encore music glossary\n")
    monkeypatch.setattr(semantic, "GLOSSARY_PATH", template)
    monkeypatch.setattr(semantic, "CORPUS_DIR", tmp_path / "none")
    assert semantic.load_documents() == []


def test_glossary_entries_become_one_chunk_each(tmp_path, monkeypatch):
    glossary = tmp_path / "glossary.md"
    glossary.write_text("# Encore music glossary\n\n## Shoegaze\nWashed-out guitars.\n\n## B-side\nThe other song.\n")
    monkeypatch.setattr(semantic, "GLOSSARY_PATH", glossary)
    monkeypatch.setattr(semantic, "CORPUS_DIR", tmp_path / "none")
    chunks = semantic.make_chunks("sections")
    assert [chunk["section"] for chunk in chunks] == ["Shoegaze", "B-side"]


# ---------------------------------------------------------------- searching

def test_keyword_tokens_keep_identifiers_whole():
    tokens = semantic.keyword_tokens("GET /1/explore/lb-radio and X-RateLimit-Reset-In")
    assert "1/explore/lb-radio" in tokens
    assert "x-ratelimit-reset-in" in tokens


def test_hybrid_search_finds_an_exact_endpoint_path():
    semantic.build("sections", [API_DOC, RATE_DOC])
    results = semantic.search("/1/explore/lb-radio", strategy="sections", k=1, hybrid=True)
    assert "lb-radio" in results[0]["text"]
    assert results[0]["url"].endswith("misc.html"), "every passage carries its source"


def test_fusion_rewards_agreement_between_the_two_searches():
    a, b, c = {"id": "a"}, {"id": "b"}, {"id": "c"}
    fused = semantic.fuse([[a, b, c], [b, c, a]], k=3)
    assert fused[0]["id"] == "b", "second in one list and first in the other beats first and last"


def test_searching_before_building_says_how_to_fix_it():
    with pytest.raises(semantic.KnowledgeBaseMissing) as error:
        semantic.search("anything")
    assert "semantic.py --build" in str(error.value)


# ---------------------------------------------------------------- the tool

def test_the_tool_returns_passages_with_sources_marked_as_data(agent_module):
    semantic.build("sections", [API_DOC, RATE_DOC])
    result = json.loads(agent_module.search_music_knowledge("What does X-RateLimit-Reset-In mean?"))
    assert result["success"]
    assert "not instructions" in result["data"]["note"]
    passage = result["data"]["passages"][0]
    assert set(passage) == {"source", "section", "url", "text"}
    assert "Reset-In" in passage["text"]


def test_the_tool_reports_a_missing_index_as_a_resource_error(agent_module):
    result = json.loads(agent_module.search_music_knowledge("shoegaze"))
    assert result["error_category"] == "resource"


def test_the_tool_rejects_an_empty_query(agent_module):
    assert json.loads(agent_module.search_music_knowledge("  "))["error_category"] == "input"
