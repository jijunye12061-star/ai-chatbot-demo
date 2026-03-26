"""
SQL 执行工具：LLM 生成的 SQL → 安全校验 → 执行 → 格式化结果
"""
import json
from db.safety import validate_sql
from db.connection import execute_query
from tools.tool_result import ToolResult
from utils.serializers import json_default

_PREVIEW_ROWS = 5  # 进入 LLM 上下文的最大行数


def execute_sql(sql: str, explanation: str = "") -> ToolResult:
    """
    执行 LLM 生成的 SQL，返回 ToolResult。
    - summary: 前 _PREVIEW_ROWS 条 + 总数，注入 LLM 上下文
    - full_rows: 行数 > _PREVIEW_ROWS 时有值，供前端 Excel 下载
    """
    print(f"[SQL] 执行SQL: {sql[:200]}")
    if explanation:
        print(f"[SQL] 目的: {explanation}")

    # 安全校验
    ok, result = validate_sql(sql)
    if not ok:
        msg = f"SQL 安全校验未通过：{result}"
        print(f"[SQL] {msg}")
        return ToolResult(summary=msg, full_rows=None, columns=None)

    sanitized_sql = result
    print(f"[SQL] 校验通过，清洗后SQL: {sanitized_sql[:200]}")

    # 执行查询
    try:
        rows = execute_query(sanitized_sql, readonly=True)
    except Exception as e:
        msg = f"SQL 执行失败：{type(e).__name__}: {e}"
        print(f"[SQL] {msg}")
        return ToolResult(summary=msg, full_rows=None, columns=None)

    if not rows:
        return ToolResult(
            summary="查询执行成功，但未找到符合条件的数据。",
            full_rows=None,
            columns=None,
        )

    total = len(rows)
    print(f"[SQL] 查询成功，返回 {total} 行")

    # 构造进入 LLM 的 summary（前5条）
    preview = rows[:_PREVIEW_ROWS]
    preview_str = json.dumps(preview, ensure_ascii=False, default=json_default, indent=2)
    if total > _PREVIEW_ROWS:
        summary = f"查询成功，共 {total} 行数据（展示前 {_PREVIEW_ROWS} 条）：\n{preview_str}"
    else:
        summary = f"查询成功，共 {total} 行数据：\n{preview_str}"

    # 行数 > _PREVIEW_ROWS 时，保留完整数据供前端 Excel 下载
    if total > _PREVIEW_ROWS:
        columns = list(rows[0].keys()) if rows else []
        full_rows = [list(row.values()) for row in rows]
    else:
        columns = None
        full_rows = None

    return ToolResult(summary=summary, full_rows=full_rows, columns=columns)
