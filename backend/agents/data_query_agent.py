"""
DataQueryAgent：数据库查询 Agent
覆盖 _load_prompt，动态注入 db_schema 内容
"""
import os
from agents.base import BaseAgent

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


class DataQueryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DataQueryAgent",
            prompt_file="data_query.md",
            tool_names=["execute_sql"],
        )

    def _load_prompt(self, filename: str) -> str:
        from datetime import date
        prompt = super()._load_prompt(filename)
        # 注入数据库结构说明
        schema_path = os.path.join(_TEMPLATES_DIR, "db_schema.md")
        with open(schema_path, "r", encoding="utf-8") as f:
            db_schema = f.read()
        today = date.today().strftime("%Y-%m-%d")
        return prompt.format(db_schema=db_schema, today=today)


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
