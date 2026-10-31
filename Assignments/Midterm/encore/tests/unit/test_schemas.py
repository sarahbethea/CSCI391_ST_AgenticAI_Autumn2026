"""Unit layer: every tool schema matches its function, so the model can't be told to send bad arguments."""

import inspect

import jsonschema
import pytest

from schemas import TOOL_SCHEMAS

SCHEMAS = {s["function"]["name"]: s["function"] for s in TOOL_SCHEMAS}


def test_every_tool_has_exactly_one_schema(agent_module):
    assert len(SCHEMAS) == len(TOOL_SCHEMAS), "duplicate schema names"
    assert set(SCHEMAS) == set(agent_module.TOOLS)


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_schema_matches_function_signature(agent_module, name):
    params = SCHEMAS[name]["parameters"]
    jsonschema.Draft202012Validator.check_schema(params)
    signature = inspect.signature(agent_module.TOOLS[name]).parameters
    assert set(params["properties"]) == set(signature), "schema properties must equal the function's parameters"
    no_default = {p for p, v in signature.items() if v.default is inspect.Parameter.empty}
    assert no_default <= set(params["required"]), "parameters without defaults must be required"


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_description_says_when_not_to_use(name):
    assert "Do not use this" in SCHEMAS[name]["description"]


@pytest.mark.parametrize("name, prop, accepted", [
    ("get_feedback", "kind", "FEEDBACK_SCORES"),
    ("set_feedback", "action", "FEEDBACK_ACTIONS"),
    ("lb_radio", "mode", "RADIO_MODES"),
    ("export_playlist", "service", "EXPORT_SERVICES"),
    ("final_answer", "status", "FINAL_STATUSES"),
    ("final_answer", "confidence", "CONFIDENCE_LEVELS"),
])
def test_enums_match_what_the_function_accepts(agent_module, name, prop, accepted):
    enum = SCHEMAS[name]["parameters"]["properties"][prop]["enum"]
    assert set(enum) == set(getattr(agent_module, accepted))
