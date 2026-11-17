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
]

TOOL_FUNCS = {
    "get_claim_status": get_claim_status,
    "get_policy_details": get_policy_details,
}
