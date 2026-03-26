# backend/tests/test_base_sse.py
"""
测试 base.py 的 SSE 事件 yield 行为（mock LLM + 工具，无需真实 API）。
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.base import BaseAgent
from tools.tool_result import ToolResult


def parse_sse_lines(lines: list[str]) -> list[dict]:
    """将 SSE 行列表解析为事件字典列表"""
    events = []
    for line in lines:
        line = line.strip()
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


async def collect_sse(agent, messages) -> list[dict]:
    lines = []
    async for line in agent.run(messages):
        lines.append(line)
    return parse_sse_lines(lines)


# ── 无工具 Agent ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_no_tools_agent_yields_content_events():
    """无工具 Agent 直接 yield content 事件"""
    with patch("agents.base.stream_text") as mock_stream:
        async def fake_stream(messages):
            for chunk in ["Hello", " world"]:
                yield chunk
        mock_stream.side_effect = fake_stream

        agent = BaseAgent("test", "main_agent.md", tool_names=[])
        events = await collect_sse(agent, [{"role": "user", "content": "hi"}])

    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) >= 2
    assert content_events[-1]["done"] is True
    assert all(e.get("type") == "content" for e in events)


# ── 有工具 Agent：普通工具（返回 str）────────────────────────────────────────

@pytest.mark.asyncio
async def test_tool_call_emits_thinking_events():
    """调用工具前后应 yield thinking 事件"""
    # mock: 第一次 chat_completion 返回 tool_call，第二次返回 stop
    tool_call = MagicMock()
    tool_call.function.name = "execute_sql"
    tool_call.function.arguments = '{"sql": "SELECT 1"}'
    tool_call.id = "call_1"

    resp1 = MagicMock()
    resp1.choices[0].finish_reason = "tool_calls"
    resp1.choices[0].message.tool_calls = [tool_call]

    resp2 = MagicMock()
    resp2.choices[0].finish_reason = "stop"
    resp2.choices[0].message.content = "查询完成"
    resp2.choices[0].message.tool_calls = None

    with patch("agents.base.chat_completion", new=AsyncMock(side_effect=[resp1, resp2])), \
         patch("agents.base.get_tool_schemas", return_value=[]), \
         patch("agents.base.get_tool_func", return_value=lambda sql: ToolResult(
             summary="共 3 行", full_rows=None, columns=None)):

        agent = BaseAgent.__new__(BaseAgent)
        agent.name = "test"
        agent.system_prompt = "You are helpful."
        agent.tool_names = ["execute_sql"]
        agent._tool_schemas = []

        events = await collect_sse(agent, [{"role": "user", "content": "查询"}])

    thinking_events = [e for e in events if e.get("type") == "thinking"]
    assert len(thinking_events) >= 2  # 至少 running + done 各一个
    statuses = {e["status"] for e in thinking_events}
    assert "running" in statuses
    assert "done" in statuses


@pytest.mark.asyncio
async def test_large_sql_result_emits_result_data():
    """execute_sql 返回 full_rows 时应 yield result_data 事件"""
    tool_call = MagicMock()
    tool_call.function.name = "execute_sql"
    tool_call.function.arguments = '{"sql": "SELECT 1"}'
    tool_call.id = "call_1"

    resp1 = MagicMock()
    resp1.choices[0].finish_reason = "tool_calls"
    resp1.choices[0].message.tool_calls = [tool_call]

    resp2 = MagicMock()
    resp2.choices[0].finish_reason = "stop"
    resp2.choices[0].message.content = "筛选完成"
    resp2.choices[0].message.tool_calls = None

    large_result = ToolResult(
        summary="共 10 行，前5条：...",
        full_rows=[[f"fund_{i}", 0.3] for i in range(10)],
        columns=["基金代码", "近1年收益"],
    )

    with patch("agents.base.chat_completion", new=AsyncMock(side_effect=[resp1, resp2])), \
         patch("agents.base.get_tool_schemas", return_value=[]), \
         patch("agents.base.get_tool_func", return_value=lambda sql: large_result):

        agent = BaseAgent.__new__(BaseAgent)
        agent.name = "test"
        agent.system_prompt = "You are helpful."
        agent.tool_names = ["execute_sql"]
        agent._tool_schemas = []

        events = await collect_sse(agent, [{"role": "user", "content": "筛选基金"}])

    result_data_events = [e for e in events if e.get("type") == "result_data"]
    assert len(result_data_events) == 1
    rd = result_data_events[0]
    assert rd["columns"] == ["基金代码", "近1年收益"]
    assert len(rd["rows"]) == 10
