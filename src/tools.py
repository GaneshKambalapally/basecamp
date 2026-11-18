import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _find(filename, key, value):
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        for record in json.load(f):
            if record[key] == value:
                return record
    return None


def get_claim_status(claim_id):
    claim = _find("claims.json", "claim_id", claim_id)
    return claim or {"error": f"Claim {claim_id} not found"}


def get_policy_details(policy_id):
    policy = _find("policies.json", "policy_id", policy_id)
    return policy or {"error": f"Policy {policy_id} not found"}


COPAY = {"Health": 0.10, "Motor": 0.05, "Life": 0.0}
APPROVAL_LIMIT = 100_000


def estimate_payout(claim_id):
    claim = get_claim_status(claim_id)
    if "error" in claim:
        return claim
    if claim["status"] != "Approved":
        return {"eligible": False, "reason": f"Claim status is {claim['status']}"}
    policy = get_policy_details(claim["policy_id"])
    if "error" in policy:
        return policy
    if not policy["active"]:
        return {"eligible": False, "reason": "Policy inactive"}
    base = min(claim["amount"], policy["sum_insured"])
    payout = round(base * (1 - COPAY[policy["type"]]))
    return {
        "eligible": True,
        "base": base,
        "payout": payout,
        "requires_approval": payout > APPROVAL_LIMIT,
    }


TOOLS = [
    {
        "name": "get_claim_status",
        "description": (
            "Look up an insurance claim by ID (format CLM-1001). Returns policy_id, "
            "status, amount, last updated date and, for rejected claims, the reason."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"claim_id": {"type": "string", "description": "e.g. CLM-1001"}},
            "required": ["claim_id"],
        },
    },
    {
        "name": "get_policy_details",
        "description": (
            "Look up an insurance policy by ID (format POL-2001). Returns holder, "
            "policy type, sum insured and whether the policy is active."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"policy_id": {"type": "string", "description": "e.g. POL-2001"}},
            "required": ["policy_id"],
        },
    },
    {
        "name": "estimate_payout",
        "description": (
            "Estimate the payout for an insurance claim by ID (format CLM-1001). "
            "Only approved claims on active policies are eligible. Returns eligible, "
            "base, payout and requires_approval, or a reason when not eligible."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"claim_id": {"type": "string", "description": "e.g. CLM-1001"}},
            "required": ["claim_id"],
        },
    },
]

TOOL_FUNCS = {
    "get_claim_status": get_claim_status,
    "get_policy_details": get_policy_details,
    "estimate_payout": estimate_payout,
}
