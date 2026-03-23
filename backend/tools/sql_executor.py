"""
SQL 执行工具：LLM 生成的 SQL → 安全校验 → 执行 → 格式化结果
"""
import json
from db.safety import validate_sql
from db.connection import execute_query
from utils.serializers import json_default


def execute_sql(sql: str, explanation: str = "") -> str:
    """
    执行 LLM 生成的 SQL。
    1. 安全校验（db/safety.py）
    2. 注入 LIMIT（safety.py 已处理）
    3. 使用只读账号执行
    4. 格式化返回结果
    """
    print(f"[SQL] 执行SQL: {sql[:200]}")
    if explanation:
        print(f"[SQL] 目的: {explanation}")

    # 安全校验
    ok, result = validate_sql(sql)
    if not ok:
        msg = f"SQL 安全校验未通过：{result}"
        print(f"[SQL] {msg}")
        return msg

    sanitized_sql = result
    print(f"[SQL] 校验通过，清洗后SQL: {sanitized_sql[:200]}")

    # 执行查询（只读账号 + 超时控制）
    try:
        rows = execute_query(sanitized_sql, readonly=True)
    except Exception as e:
        msg = f"SQL 执行失败：{type(e).__name__}: {e}"
        print(f"[SQL] {msg}")
        return msg

    if not rows:
        return "查询执行成功，但未找到符合条件的数据。"

    result_str = json.dumps(rows, ensure_ascii=False, default=json_default, indent=2)
    row_count = len(rows)
    print(f"[SQL] 查询成功，返回 {row_count} 行")

    return f"查询成功，共 {row_count} 行数据：\n{result_str}"
