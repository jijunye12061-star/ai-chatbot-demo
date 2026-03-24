"""
跨区间多条件业绩筛选。

模板 004 (type=python_func) 的执行函数。
根据 conditions 中涉及的区间数量动态生成多 JOIN SQL，
每个区间对应一个 tb_fd_perform_abs 的 JOIN 别名（p00/p01/...）。
所有值均参数化传递（%s），不做字符串拼接。
"""
from db.connection import execute_query
from db.safety import validate_sql
from tools.fund_filter import ALLOWED_CONDITION_FIELDS, PERIOD_MAP, _resolve_trade_date

# 区间代码 -> 列名后缀
PERIOD_SUFFIX = {
    "00": "1m", "01": "3m", "02": "6m", "03": "1y",
    "04": "2y", "05": "3y", "06": "5y", "07": "ytd", "08": "si",
}


def cross_period_filter(
    trade_date: str = "latest",
    conditions: dict = None,
    fund_category_code: str = None,
    order_by: str = None,
    limit: int = 50,
) -> list:
    """
    跨区间多条件业绩筛选。

    参数（经 _validate_params 校验后传入）：
    - trade_date: 截止日期字符串（已解析，非 'latest'）
    - conditions: {区间名称: {字段: {min, max}}}，区间名已经过校验
    - fund_category_code: 基金一级分类代码，如 '001'（可选）
    - order_by: '区间名称.字段名'（可选）
    - limit: 返回条数
    """
    if not conditions:
        raise ValueError("conditions 不能为空")

    # 1. 解析 trade_date
    actual_date = _resolve_trade_date(trade_date) if trade_date == "latest" else trade_date

    # 2. 收集涉及的区间，按 period_code 排序保证 SQL 稳定
    involved = {}  # {period_code: (alias, period_name)}
    for period_name, _ in conditions.items():
        code = PERIOD_MAP[period_name]
        alias = f"p{code}"
        involved[code] = (alias, period_name)

    # 3. 构建 SELECT 列
    select_cols = [
        "b.c_fd_code",
        "b.c_short_name",
        "cat.c_type1_name",
        "cat.c_type2_name",
    ]
    for code in sorted(involved):
        alias, period_name = involved[code]
        suffix = PERIOD_SUFFIX[code]
        # 固定展示 c_period_ret（区间收益率）
        select_cols.append(f"{alias}.c_period_ret AS period_ret_{suffix}")
        # 添加条件中用到的字段（跳过已加入的 c_period_ret）
        for field in conditions[period_name]:
            if field != "c_period_ret":
                col_alias = field[2:] if field.startswith("c_") else field  # c_ann_ret -> ann_ret
                select_cols.append(f"{alias}.{field} AS {col_alias}_{suffix}")

    # 4. 构建 JOIN 子句和对应的 params
    params = []
    join_lines = []
    for code in sorted(involved):
        alias, _ = involved[code]
        join_lines.append(
            f"JOIN tb_fd_perform_abs {alias}"
            f" ON {alias}.c_fd_code = b.c_fd_code"
            f" AND {alias}.c_trade_date = %s AND {alias}.c_period_code = %s"
        )
        params.extend([actual_date, code])

    # 5. category 子查询（取最新一期分类数据）
    cat_join = (
        "LEFT JOIN (\n"
        "    SELECT c_fd_code, c_type1_name, c_type1_code, c_type2_name,\n"
        "           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn\n"
        "    FROM tb_fd_category\n"
        ") cat ON b.c_fd_code = cat.c_fd_code AND cat.rn = 1"
    )

    # 6. WHERE 条件
    where_parts = ["1=1"]
    for period_name, field_conditions in conditions.items():
        code = PERIOD_MAP[period_name]
        alias = f"p{code}"
        for field, bounds in field_conditions.items():
            if bounds.get("min") is not None:
                where_parts.append(f"{alias}.{field} >= %s")
                params.append(bounds["min"])
            if bounds.get("max") is not None:
                where_parts.append(f"{alias}.{field} <= %s")
                params.append(bounds["max"])

    if fund_category_code:
        where_parts.append("cat.c_type1_code = %s")
        params.append(fund_category_code)

    # 7. ORDER BY
    order_clause = _parse_order_by(order_by, conditions)

    # 8. LIMIT
    params.append(limit)

    # 9. 组装 SQL
    sql = (
        f"SELECT {', '.join(select_cols)}\n"
        f"FROM tb_fd_basic_info b\n"
        + "\n".join(join_lines) + "\n"
        + cat_join + "\n"
        f"WHERE {' AND '.join(where_parts)}\n"
        f"ORDER BY {order_clause}\n"
        f"LIMIT %s"
    )

    # 10. 安全校验
    ok, result = validate_sql(sql)
    if not ok:
        raise ValueError(f"SQL 安全校验失败: {result}")

    return execute_query(result, params=tuple(params), readonly=True)


def _parse_order_by(order_by: str, conditions: dict) -> str:
    """解析 order_by 参数，返回 ORDER BY 子句片段（不含 ORDER BY 关键字）。"""
    if order_by and "." in order_by:
        parts = order_by.split(".", 1)
        period_name, field = parts[0], parts[1]
        if period_name in PERIOD_MAP and field in ALLOWED_CONDITION_FIELDS:
            alias = f"p{PERIOD_MAP[period_name]}"
            return f"{alias}.{field} DESC"
    # 默认：第一个条件区间的 c_ann_ret 降序
    first_period = next(iter(conditions))
    first_alias = f"p{PERIOD_MAP[first_period]}"
    return f"{first_alias}.c_ann_ret DESC"
