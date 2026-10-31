"""Unit layer: procedural memory (prompts/system_v1.md) and how it reaches every model call."""

import pytest

WORD_LIMIT = 700


@pytest.fixture
def prompt_text(agent_module):
    return agent_module.SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def test_prompt_is_within_the_word_limit(prompt_text):
    assert len(prompt_text.split()) <= WORD_LIMIT


def test_every_section_is_present(agent_module, prompt_text):
    for heading in ("Role", "Rules", "Memory", "Tools"):
        section = agent_module.prompt_section(prompt_text, heading)
        assert section.startswith(f"# {heading}")
        assert len(section.splitlines()) > 1, f"the {heading} section has a heading but no content"


def test_section_stops_at_the_next_heading(agent_module):
    text = "# Role\nYou are Encore.\n# Rules\n- Rule one.\n- Rule two.\n# Memory\nRemember things."
    assert agent_module.prompt_section(text, "Rules") == "# Rules\n- Rule one.\n- Rule two."


def test_missing_section_fails_loudly(agent_module):
    with pytest.raises(ValueError):
        agent_module.prompt_section("# Role\nYou are Encore.", "Rules")


def test_rules_come_first_and_history_last(agent_module):
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    messages = agent_module.build_messages("RULES", "GUIDANCE", "hi", history)
    assert messages[0] == {"role": "system", "content": "RULES"}
    assert messages[1] == {"role": "system", "content": "GUIDANCE"}
    assert messages[2] == {"role": "system", "content": "Current request: hi"}
    assert messages[-2:] == history


def test_build_messages_does_not_change_history(agent_module):
    history = [{"role": "user", "content": "hi"}]
    agent_module.build_messages("RULES", "GUIDANCE", "hi", history)
    assert history == [{"role": "user", "content": "hi"}], "rules must never be stored in history"
