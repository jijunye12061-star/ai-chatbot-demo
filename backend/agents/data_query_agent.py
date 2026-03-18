"""
DataQueryAgent：数据库查询 Agent
两层召回：始终注入 table_catalog，按需通过 get_table_schema 获取详细字段说明
"""
import os
from agents.base import BaseAgent

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


class DataQueryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DataQueryAgent",
            prompt_file="data_query.md",
            tool_names=["get_table_schema", "execute_sql"],
        )

    def _load_prompt(self, filename: str) -> str:
        from datetime import date
        prompt = super()._load_prompt(filename)
        # 注入表目录（轻量级，始终注入）
        catalog_path = os.path.join(_TEMPLATES_DIR, "table_catalog.md")
        with open(catalog_path, "r", encoding="utf-8") as f:
            table_catalog = f.read()
        today = date.today().strftime("%Y-%m-%d")
        return prompt.format(table_catalog=table_catalog, today=today)


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "查一下000001最近一周的净值"

    async def main():
        agent = DataQueryAgent()
        async for chunk in agent.run([{"role": "user", "content": query}]):
            print(chunk, end="", flush=True)
        print()

    asyncio.run(main())
