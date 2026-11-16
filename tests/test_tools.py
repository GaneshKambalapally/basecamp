import inspect

from tools import TOOLS, TOOL_FUNCS, get_claim_status, get_policy_details


def test_claim_found():
    claim = get_claim_status("CLM-1004")
    assert claim["status"] == "Rejected"
    assert claim["policy_id"] == "POL-2002"


def test_claim_not_found():
    assert "error" in get_claim_status("CLM-9999")


def test_policy_found():
    policy = get_policy_details("POL-2004")
    assert policy["holder"] == "Sneha Reddy"
    assert policy["active"] is False


def test_policy_not_found():
    assert "error" in get_policy_details("POL-9999")


def test_schemas_match_functions():
    assert {t["name"] for t in TOOLS} == set(TOOL_FUNCS)
    for tool in TOOLS:
        params = list(inspect.signature(TOOL_FUNCS[tool["name"]]).parameters)
        assert tool["input_schema"]["required"] == params
