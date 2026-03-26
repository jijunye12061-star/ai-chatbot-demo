# backend/agents/base.py
"""
BaseAgent：所有 Agent 的基类
实现 Function Calling 循环：
  1. 非流式调用（带 tools）→ 检测 tool_calls
  2. 有 tool_calls → 执行工具 → 结果塞回 messages → 回到 1
  3. 无 tool_calls → 流式调用输出最终回复
yield 格式：预格式化的 SSE 行（data: {...}\n\n），由 orchestrator 透传至 api/chat.py
"""
import asyncio
import inspect
import json
import os
from typing import AsyncGenerator

from llm.client import chat_completion, stream_text
from tools.registry import get_tool_schemas, get_tool_func
from tools.tool_result import ToolResult
from utils.conv_logger import get_conv_logger

_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

# 工具名称 → 用户可读的中文描述（用于 thinking 步骤文案）
_TOOL_DISPLAY_NAMES = {
    "execute_sql": "查询数据库",
    "get_table_schema": "读取表结构",
    "get_dimension_list": "获取维度列表",
    "get_screen_guide": "加载筛选知识",
    "generate_fund_report": "生成基金报告",
}


def _sse(payload: dict) -> str:
    """序列化为完整 SSE 行"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _thinking(step: str, status: str) -> str:
    return _sse({"type": "thinking", "step": step, "status": status})


def _content(text: str, done: bool = False) -> str:
    return _sse({"type": "content", "content": text, "done": done})


class BaseAgent:
    def __init__(self, name: str, prompt_file: str, tool_names: list = None):
        self.name = name
        self.system_prompt = self._load_prompt(prompt_file)
        self.tool_names = tool_names or []
        self._tool_schemas = get_tool_schemas(self.tool_names) if self.tool_names else []

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(_PROMPTS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def run(self, messages: list) -> AsyncGenerator[str, None]:
        """
        主执行循环。yield 预格式化的 SSE 行字符串。
        """
        full_messages = [{"role": "system", "content": self.system_prompt}] + list(messages)

        # 快速路径：无工具 Agent 直接流式输出
        if not self.tool_names:
            async for chunk in stream_text(full_messages):
                yield _content(chunk)
            yield _content("", done=True)
            return

        max_iterations = 10
        for _ in range(max_iterations):
            response = await chat_completion(
                full_messages,
                tools=self._tool_schemas,
                stream=False,
            )
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                tool_calls = choice.message.tool_calls
                full_messages.append(choice.message)

                for tc in tool_calls:
                    tool_name = tc.function.name
                    display = _TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
                    print(f"[{self.name}] 调用工具: {tool_name}, args: {tc.function.arguments[:200]}")

                    _log = get_conv_logger()
                    if _log:
                        _log.tool_call(tool_name, tc.function.arguments)

                    # 思考步骤：开始
                    yield _thinking(step=f"正在{display}...", status="running")

                    result = await self._execute_tool(tool_name, tc.function.arguments)

                    if isinstance(result, ToolResult):
                        # 思考步骤：完成
                        yield _thinking(step=f"{display}完成", status="done")
                        if _log:
                            _log.tool_result(tool_name, result.summary)
                        # result_data 旁路：完整数据直达前端，不进 LLM
                        if result.has_full_data:
                            yield _sse({
                                "type": "result_data",
                                "columns": result.columns,
                                "rows": result.full_rows,
                            })
                        tool_content = result.summary
                    else:
                        # 非 ToolResult（其他工具返回 str）
                        if isinstance(result, str) and result.startswith("[工具执行错误]"):
                            yield _thinking(step=f"{display}失败", status="error")
                        else:
                            yield _thinking(step=f"{display}完成", status="done")
                        if _log:
                            _log.tool_result(tool_name, str(result))
                        tool_content = str(result)

                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_content,
                    })
                continue

            else:
                # finish_reason == "stop"
                yield _content(choice.message.content or "")
                yield _content("", done=True)
                break
        else:
            print(f"[{self.name}] ⚠️ FC 循环达到上限 {max_iterations}")
            yield _content("抱歉，处理过程过于复杂，请尝试简化问题。")
            yield _content("", done=True)

    async def _execute_tool(self, tool_name: str, arguments: str):
        """执行工具，返回 ToolResult 或 str"""
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError:
            return f"[错误] 无法解析工具参数：{arguments}"

        func = get_tool_func(tool_name)
        if func is None:
            return f"[错误] 未找到工具：{tool_name}"

        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**args)
            else:
                result = await asyncio.to_thread(func, **args)
            return result
        except Exception as e:
            return f"[工具执行错误] {tool_name}: {type(e).__name__}: {e}"
