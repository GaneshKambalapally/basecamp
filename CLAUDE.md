
## Stack
- Python 3.11+ (venv in `.venv`, currently 3.14), anthropic SDK, mcp, python-dotenv, pytest. No other dependencies.
- Model: claude-sonnet-5-5 (set once in src/agent.py as MODEL)
- Platform: Windows. Use `.venv\Scripts\python`.
- API key lives in `.env` as ANTHROPIC_API_KEY, loaded with python-dotenv.

## Layout
Current:
- hello.py: one-call Anthropic smoke test
- requirements.txt: anthropic, mcp, python-dotenv, pytest

Planned (not created yet, don't assume they exist):
- src/tools.py: plain functions + TOOLS schema list
- src/agent.py: run_agent(question) loop + trace
- src/mcp_server.py: MCP server exposing the same tools
- data/: read-only JSON test data. Never modify.
- tests/: pytest. Mock the Anthropic API, so tests never call the real API.

## Commands
- Smoke test: `.venv\Scripts\python hello.py`
- Tests: `.venv\Scripts\python -m pytest -q`

## Rules
- Smallest change for the current step only. Ask if unclear.
- Plain functions, no classes unless I ask.
- Every change comes with a test. Run `pytest -q` after each change.
- Never edit .env, .gitignore or data/.
- Never run git push, git reset or pip install without asking.
- End each change with a 3-bullet summary.
