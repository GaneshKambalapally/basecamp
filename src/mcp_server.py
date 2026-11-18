"""MCP server exposing the claims tools over stdio.

Run from the project root with: python -m src.mcp_server
"""
from mcp.server.mcpserver import MCPServer

from src.tools import TOOL_FUNCS, TOOLS

mcp = MCPServer("securelife-claims")

for tool in TOOLS:
    mcp.add_tool(TOOL_FUNCS[tool["name"]], name=tool["name"], description=tool["description"])

if __name__ == "__main__":
    mcp.run(transport="stdio")
