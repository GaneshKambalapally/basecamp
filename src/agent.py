import json
import sys

import anthropic
from dotenv import load_dotenv

from src.tools import TOOLS, TOOL_FUNCS

load_dotenv()

MODEL = "claude-sonnet-5-5"
MAX_TURNS = 6
PREVIEW_CHARS = 80
TOOL_MAP = TOOL_FUNCS
client = anthropic.Anthropic()


def _trace(turn, response, results):
    usage = response.usage
    print(
        f"[turn {turn}/{MAX_TURNS}] stop_reason={response.stop_reason}  "
        f"tokens in={usage.input_tokens} out={usage.output_tokens}"
    )
    previews = {r["tool_use_id"]: r["content"] for r in results}
    for block in response.content:
        if block.type != "tool_use":
            continue
        print(f"  tool: {block.name}({block.input})")
        content = previews[block.id]
        if len(content) > PREVIEW_CHARS:
            content = content[:PREVIEW_CHARS] + "..."
        print(f"    result: {content}")


def run_agent(question):
    messages = [{"role": "user", "content": question}]
    for turn in range(1, MAX_TURNS + 1):
        response = client.messages.create(
            model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages
        )
        if response.stop_reason != "tool_use":
            _trace(turn, response, [])
            return "".join(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            func = TOOL_MAP.get(block.name)
            if func is None:
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Unknown tool: {block.name}",
                    "is_error": True,
                })
            else:
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(func(**block.input)),
                })
        _trace(turn, response, results)
        messages.append({"role": "user", "content": results})
    return f"Stopped after {MAX_TURNS} turns without a final answer."


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Usage: python -m src.agent "your question"')
        sys.exit(1)
    print(run_agent(question))
