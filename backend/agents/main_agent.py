"""
MainAgent：合并 RouterAgent + ChatAgent + DataQueryAgent + FundScreenerAgent
挂载全部工具，单次 LLM 调用起步。
"""
import os
from datetime import date
from agents.base import BaseAgent


class MainAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MainAgent",
            prompt_file="main_agent.md",  # BaseAgent 正常加载原始模板
            tool_names=[
                "get_table_schema",
                "execute_sql",
                "get_screen_guide",
                "get_dimension_list",
                "ask_report_agent",
            ],
        )
        # 覆盖 system_prompt：填充 {table_catalog}、{screen_catalog}、{today}
        self.system_prompt = self._inject_catalogs(self.system_prompt)

    def _inject_catalogs(self, template: str) -> str:
        base_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        with open(os.path.join(base_dir, "table_catalog.md"), "r", encoding="utf-8") as f:
            table_catalog = f.read()
        with open(os.path.join(base_dir, "screen_catalog.md"), "r", encoding="utf-8") as f:
            screen_catalog = f.read()
        return template.format(
            today=date.today().isoformat(),
            table_catalog=table_catalog,
            screen_catalog=screen_catalog,
        )
