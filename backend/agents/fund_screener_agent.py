"""
FundScreenerAgent：基金筛选 Agent
"""
from agents.base import BaseAgent


class FundScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FundScreenerAgent",
            prompt_file="fund_screener.md",
            tool_names=["filter_funds"],
        )


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "筛选规模大于50亿的股票型基金，近一年收益率超过10%"

    async def main():
        agent = FundScreenerAgent()
        async for chunk in agent.run([{"role": "user", "content": query}]):
            print(chunk, end="", flush=True)
        print()

    asyncio.run(main())
