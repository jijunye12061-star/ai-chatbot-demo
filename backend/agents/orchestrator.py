"""
Orchestrator：总调度入口（简化版）
直接调用 MainAgent，无路由层。
yield: 预格式化的 SSE 行字符串（由 base.py 生成，此处透传）
"""
from typing import AsyncGenerator
from agents.main_agent import MainAgent

_agent = MainAgent()


async def run(message: str, history: list) -> AsyncGenerator[str, None]:
    """
    总调度入口。
    yield: 完整 SSE 行，格式 "data: {...}\n\n"
    """
    messages = list(history) + [{"role": "user", "content": message}]
    async for sse_line in _agent.run(messages):
        yield sse_line


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "什么是夏普比率"

    async def main():
        async for chunk in run(query, []):
            print(chunk, end="", flush=True)
        print()

    asyncio.run(main())
