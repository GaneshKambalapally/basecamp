import asyncio

from src.mcp_server import mcp


def test_tools_registered():
    tools = asyncio.run(mcp.list_tools())
    assert {t.name for t in tools} == {"get_claim_status", "get_policy_details", "estimate_payout"}
