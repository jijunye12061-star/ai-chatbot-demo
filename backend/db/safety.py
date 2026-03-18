"""
SQL 安全校验模块（硬性防护）
校验顺序：去注释 → 单语句 → SELECT only → 白名单表 → 子查询深度 → LIMIT 注入
"""
import re
import sqlparse

ALLOWED_TABLES = {
    "tb_fd_basic_info",
    "tb_fd_category",
    "tb_fd_nav_daily",
    "tb_fd_asset_allocation",
    "tb_fd_portfolio_bd",
    "tb_fd_portfolio_stk",
    "tb_fd_perform_abs",
    "tb_dict_params",
    "tb_fd_tag_asset_eq",
}

MAX_ROWS = 1000


def validate_sql(sql: str) -> tuple:
    """
    校验并清洗 SQL。
    返回 (True, sanitized_sql) 或 (False, error_message)
    """
    # 1. 去除注释
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    sql = sql.strip()

    if not sql:
        return False, "SQL 为空"

    # 2. 检测危险关键词（防止注释注入后遗留 DML/DDL）
    _DANGEROUS = re.compile(
        r"\b(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE|GRANT|REVOKE)\b",
        re.IGNORECASE,
    )
    danger_match = _DANGEROUS.search(sql)
    if danger_match:
        return False, f"检测到危险关键词：{danger_match.group()}"

    # 3. 禁止多语句注入（分号出现在末尾之前）
    stripped = sql.rstrip(";")
    if ";" in stripped:
        return False, "不允许多条 SQL 语句（检测到分号）"
    sql = stripped

    # 4. 使用 sqlparse 解析，只允许 SELECT
    parsed = sqlparse.parse(sql)
    if not parsed:
        return False, "无法解析 SQL"
    stmt_type = parsed[0].get_type()
    if stmt_type != "SELECT":
        return False, f"只允许 SELECT 语句，检测到：{stmt_type or '未知类型'}"

    # 5. 提取表名，校验白名单
    tables = _extract_tables(sql)
    if not tables:
        return False, "未找到查询的表名"
    for t in tables:
        if t.lower() not in ALLOWED_TABLES:
            return False, f"表 '{t}' 不在白名单中，允许的表：{', '.join(sorted(ALLOWED_TABLES))}"

    # 6. 子查询深度 ≤ 2
    depth = _subquery_depth(sql)
    if depth > 2:
        return False, f"子查询嵌套过深（{depth} 层），最大允许 2 层"

    # 7. 注入 LIMIT（如缺失）
    if not re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
        sql = f"{sql} LIMIT {MAX_ROWS}"

    return True, sql


def _extract_tables(sql: str) -> list:
    """从 SQL 中提取 FROM / JOIN 后的表名"""
    pattern = r"\b(?:FROM|JOIN)\s+([`\"]?[a-zA-Z_][a-zA-Z0-9_]*[`\"]?)"
    matches = re.findall(pattern, sql, re.IGNORECASE)
    return [m.strip("`\"") for m in matches]


def _subquery_depth(sql: str) -> int:
    """计算括号最大嵌套深度（近似子查询深度）"""
    max_depth = 0
    depth = 0
    in_string = False
    quote_char = None
    for char in sql:
        if in_string:
            if char == quote_char:
                in_string = False
        elif char in ("'", '"', "`"):
            in_string = True
            quote_char = char
        elif char == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == ")":
            depth -= 1
    return max_depth
