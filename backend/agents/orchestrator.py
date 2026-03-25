"""
Orchestrator：总调度入口（简化版）
直接调用 MainAgent，无路由层。
"""
from typing import AsyncGenerator
from agents.main_agent import MainAgent

_agent = MainAgent()


async def run(message: str, history: list) -> AsyncGenerator[str, None]:
    """
    总调度入口。
    history: [{"role": "user"/"assistant", "content": "..."}]
    yield: str 文本片段
    """
    messages = list(history) + [{"role": "user", "content": message}]
    async for chunk in _agent.run(messages):
        yield chunk


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "什么是夏普比率"

    async def main():
        async for chunk in run(query, []):
            print(chunk, end="", flush=True)
        print()

    asyncio.run(main())
