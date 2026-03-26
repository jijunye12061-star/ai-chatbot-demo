from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolResult:
    """
    sql_executor 的结构化返回值。
    summary: 前5条 + 总数的 Markdown 表格文本，注入 LLM 上下文。
    full_rows: 完整行数据（行数>5时有值），仅供前端 Excel 下载，不进 LLM。
    columns: 列名列表，与 full_rows 配套使用。
    """
    summary: str
    full_rows: Optional[list]
    columns: Optional[list]

    @property
    def has_full_data(self) -> bool:
        return self.full_rows is not None
