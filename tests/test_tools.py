import inspect

import pytest

from src import tools
from src.tools import TOOLS, TOOL_FUNCS, estimate_payout, get_claim_status, get_policy_details


@pytest.fixture
def setup(monkeypatch):
    def _setup(ptype="Health", amount=50_000, sum_insured=200_000, status="Approved", active=True):
        claim = {"claim_id": "CLM-1", "policy_id": "POL-1", "status": status, "amount": amount}
        policy = {"policy_id": "POL-1", "type": ptype, "sum_insured": sum_insured, "active": active}

        def fake_find(filename, key, value):
            record = claim if filename == "claims.json" else policy
            return record if record[key] == value else None

        monkeypatch.setattr(tools, "_find", fake_find)

    return _setup


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


def test_payout_health(setup):
    setup("Health", 50_000, 200_000)
    result = estimate_payout("CLM-1")
    assert result["eligible"] is True
    assert result["payout"] == 45_000
    assert result["requires_approval"] is False


def test_payout_motor(setup):
    setup("Motor", 40_000)
    assert estimate_payout("CLM-1")["payout"] == 38_000


def test_payout_life(setup):
    setup("Life", 80_000)
    assert estimate_payout("CLM-1")["payout"] == 80_000


def test_payout_under_review(setup):
    setup(status="Under Review")
    result = estimate_payout("CLM-1")
    assert result["eligible"] is False
    assert "Under Review" in result["reason"]


def test_payout_rejected(setup):
    setup(status="Rejected")
    assert estimate_payout("CLM-1")["eligible"] is False


def test_payout_inactive_policy(setup):
    setup(active=False)
    result = estimate_payout("CLM-1")
    assert result["eligible"] is False
    assert result["reason"] == "Policy inactive"


def test_payout_unknown_claim():
    assert "not found" in estimate_payout("CLM-9999")["error"]


def test_payout_above_sum_insured(setup):
    setup("Health", 300_000, 200_000)
    result = estimate_payout("CLM-1")
    assert result["base"] == 200_000
    assert result["payout"] == 180_000


@pytest.mark.parametrize("amount,needs_approval", [(100_001, True), (100_000, False), (99_999, False)])
def test_approval_boundary(setup, amount, needs_approval):
    setup("Life", amount, 5_000_000)
    result = estimate_payout("CLM-1")
    assert result["payout"] == amount
    assert result["requires_approval"] is needs_approval
