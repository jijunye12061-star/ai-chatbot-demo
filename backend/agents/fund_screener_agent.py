"""
FundScreenerAgent：基金筛选 Agent
注入 screen_catalog，使用 run_screen_template 工具
"""
import os
from datetime import date
from agents.base import BaseAgent

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


class FundScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FundScreenerAgent",
            prompt_file="fund_screener.md",
            tool_names=["run_screen_template", "get_dimension_list", "ask_data_agent"],
        )

    def _load_prompt(self, filename: str) -> str:
        prompt = super()._load_prompt(filename)
        catalog_path = os.path.join(_TEMPLATES_DIR, "screen_catalog.md")
        with open(catalog_path, "r", encoding="utf-8") as f:
            screen_catalog = f.read()
        today = date.today().strftime("%Y-%m-%d")
        return prompt.format(screen_catalog=screen_catalog, today=today)


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "筛选近3月收益率前50的主动权益基金"

    async def main():
        agent = FundScreenerAgent()
        async for chunk in agent.run([{"role": "user", "content": query}]):
            print(chunk, end="", flush=True)
        print()

    asyncio.run(main())
