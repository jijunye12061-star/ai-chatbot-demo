"""
BaseAgent：所有 Agent 的基类
实现 Function Calling 循环：
  1. 非流式调用（带 tools）→ 检测 tool_calls
  2. 有 tool_calls → 执行工具 → 结果塞回 messages → 回到 1
  3. 无 tool_calls → 流式调用输出最终回复
"""
import asyncio
import inspect
import json
import os
from typing import AsyncGenerator

from llm.client import chat_completion, stream_text
from tools.registry import get_tool_schemas, get_tool_func

# prompts 目录相对于 backend/ 的路径
_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


class BaseAgent:
    def __init__(self, name: str, prompt_file: str, tool_names: list = None):
        self.name = name
        self.system_prompt = self._load_prompt(prompt_file)
        self.tool_names = tool_names or []

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(_PROMPTS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def run(self, messages: list) -> AsyncGenerator[str, None]:
        """
        主执行循环。yield str chunks（最终回复的文本片段）。
        messages 格式：[{"role": "user"/"assistant", "content": "..."}]
        """
        full_messages = [{"role": "system", "content": self.system_prompt}] + list(messages)
        tool_schemas = get_tool_schemas(self.tool_names) if self.tool_names else None

        max_iterations = 10
        for _ in range(max_iterations):
            # 非流式调用，用于检测 tool_calls
            response = await chat_completion(
                full_messages,
                tools=tool_schemas or None,
                stream=False,
            )
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                # 执行工具
                tool_calls = choice.message.tool_calls
                # 先把 assistant 消息加入历史
                full_messages.append(choice.message)

                for tc in tool_calls:
                    tool_name = tc.function.name
                    print(f"[{self.name}] 调用工具: {tool_name}, args: {tc.function.arguments[:200]}")
                    result = await self._execute_tool(tool_name, tc.function.arguments)
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result),
                    })
                continue  # 继续 FC 循环

            else:
                # 最终文本回复 — 流式输出
                # 如果上一轮有 tool 调用，full_messages 已包含工具结果，需要再次请求
                async for chunk in stream_text(full_messages):
                    yield chunk
                break

    async def _execute_tool(self, tool_name: str, arguments: str) -> str:
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
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: func(**args))
            return result
        except Exception as e:
            return f"[工具执行错误] {tool_name}: {type(e).__name__}: {e}"
