"""
Orchestrator：总调度入口
流程：message + history → RouterAgent 识别意图 → 分发到具体 Agent → yield SSE chunks
"""
from typing import AsyncGenerator

from agents.router_agent import RouterAgent
from agents.chat_agent import ChatAgent

# Phase B 启用
from agents.data_query_agent import DataQueryAgent

# Phase C 启用
from agents.fund_screener_agent import FundScreenerAgent

# Phase D 启用
from agents.report_agent import ReportAgent

_router = RouterAgent()

_agents = {
    "chat": ChatAgent(),
    "data_query": DataQueryAgent(),     # Phase B
    "fund_screen": FundScreenerAgent(), # Phase C
    "report": ReportAgent(),            # Phase D
}


async def run(message: str, history: list) -> AsyncGenerator[str, None]:
    """
    总调度入口。
    history: [{"role": "user"/"assistant", "content": "..."}]
    yield: str 文本片段
    """
    messages = list(history) + [{"role": "user", "content": message}]

    try:
        intent = await _router.classify(messages)
    except Exception as e:
        print(f"[Orchestrator] 路由失败: {e}，降级到 chat")
        intent = "chat"
    # _agents.get 提供第二层保护：即使 intent 不合法也回退到 chat
    agent = _agents.get(intent, _agents["chat"])
    print(f"[Orchestrator] 分发到: {agent.name}")

    async for chunk in agent.run(messages):
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
