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
        self._tool_schemas = get_tool_schemas(self.tool_names) if self.tool_names else []

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

        # 快速路径：无工具 Agent 直接流式输出，省去一次非流式调用
        if not self.tool_names:
            async for chunk in stream_text(full_messages):
                yield chunk
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
                # OpenAI 要求 assistant 消息先入列，tool 结果再追加，顺序不可颠倒
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
                continue

            else:
                # finish_reason == "stop"：内容已在非流式响应里，直接 yield，
                # 避免再次流式调用时 DeepSeek 输出 raw tool-call special tokens
                yield choice.message.content or ""
                break
        else:
            # FC 循环跑满未 break — 兜底提示，防止空回复
            print(f"[{self.name}] ⚠️ FC 循环达到上限 {max_iterations}")
            yield "抱歉，处理过程过于复杂，请尝试简化问题。"

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
                result = await asyncio.to_thread(func, **args)
            return result
        except Exception as e:
            return f"[工具执行错误] {tool_name}: {type(e).__name__}: {e}"
