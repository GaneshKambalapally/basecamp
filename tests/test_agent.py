from types import SimpleNamespace

from src import agent


def text(s):
    return SimpleNamespace(type="text", text=s)


def tool_use(id, name, **inp):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=inp)


def reply(stop_reason, *blocks):
    usage = SimpleNamespace(input_tokens=100, output_tokens=20)
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks), usage=usage)


def fake_create(monkeypatch, responses):
    calls = []

    def create(**kwargs):
        calls.append(list(kwargs["messages"]))
        return responses.pop(0) if len(responses) > 1 else responses[0]

    monkeypatch.setattr(agent.client.messages, "create", create)
    return calls


def test_one_tool_call_then_answer(monkeypatch):
    calls = fake_create(monkeypatch, [
        reply("tool_use", tool_use("t1", "get_claim_status", claim_id="CLM-1004")),
        reply("end_turn", text("CLM-1004 was rejected.")),
    ])
    assert agent.run_agent("Status of CLM-1004?") == "CLM-1004 was rejected."
    assert len(calls) == 2
    result = calls[1][-1]["content"][0]
    assert calls[1][-1]["role"] == "user"
    assert result["tool_use_id"] == "t1"
    assert "Rejected" in result["content"]


def test_max_turns_stop(monkeypatch):
    calls = fake_create(monkeypatch, [
        reply("tool_use", tool_use("t1", "get_claim_status", claim_id="CLM-1001")),
    ])
    out = agent.run_agent("loop forever")
    assert len(calls) == 6
    assert out == "Stopped after 6 turns without a final answer."


def test_trace_output(monkeypatch, capsys):
    fake_create(monkeypatch, [
        reply("tool_use", tool_use("t1", "get_claim_status", claim_id="CLM-1004")),
        reply("end_turn", text("done")),
    ])
    agent.run_agent("Status of CLM-1004?")
    out = capsys.readouterr().out
    assert "[turn 1/6] stop_reason=tool_use" in out
    assert "[turn 2/6] stop_reason=end_turn" in out
    assert "tokens in=100 out=20" in out
    assert "get_claim_status({'claim_id': 'CLM-1004'})" in out
    assert "Rejected" in out


def test_trace_truncates_long_result(monkeypatch, capsys):
    monkeypatch.setitem(agent.TOOL_MAP, "long_tool", lambda: "x" * 500)
    fake_create(monkeypatch, [
        reply("tool_use", tool_use("t1", "long_tool")),
        reply("end_turn", text("done")),
    ])
    agent.run_agent("q")
    line = [l for l in capsys.readouterr().out.splitlines() if "result:" in l][0]
    assert line.endswith("...")
    assert len(line) < 120
