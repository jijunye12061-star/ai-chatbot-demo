"""
基金筛选工具：按条件拼 SQL 直查 DB（代码生成 SQL，不走 LLM，不走 safety.py）
"""
import json
import decimal
import datetime
from db.connection import execute_query


def filter_funds(
    fund_type: str = None,
    min_size_billion: float = None,
    max_size_billion: float = None,
    min_return_1y_pct: float = None,
    limit: int = 20,
) -> str:
    """
    按条件筛选基金。
    - fund_type: 基金类型关键词（模糊匹配 c_class1_name/c_class2_name）
    - min_size_billion: 规模下限（亿元）
    - max_size_billion: 规模上限（亿元）
    - min_return_1y_pct: 近一年收益率下限（%），内部转换为小数
    """
    limit = min(limit or 20, 100)

    # 构建 JOIN 查询
    conditions = ["b.c_fd_code = n.c_fd_code"]
    params = []

    # 基金类型过滤（匹配分类名称）
    if fund_type:
        conditions.append(
            "(b.c_class1_name LIKE %s OR b.c_class2_name LIKE %s OR b.c_class3_name LIKE %s)"
        )
        like_val = f"%{fund_type}%"
        params.extend([like_val, like_val, like_val])

    # 规模过滤（需要关联资产配置表获取最新规模）
    size_join = ""
    if min_size_billion is not None or max_size_billion is not None:
        size_join = """
        LEFT JOIN (
            SELECT c_fd_code, c_fund_nav_total,
                   ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
            FROM tb_fd_asset_allocation
        ) a ON b.c_fd_code = a.c_fd_code AND a.rn = 1
        """
        if min_size_billion is not None:
            # 亿元转换为元（×1e8）
            conditions.append("a.c_fund_nav_total >= %s")
            params.append(min_size_billion * 1e8)
        if max_size_billion is not None:
            conditions.append("a.c_fund_nav_total <= %s")
            params.append(max_size_billion * 1e8)

    # 收益率过滤（使用最新一条净值记录）
    if min_return_1y_pct is not None:
        conditions.append("n.c_ret_1y >= %s")
        params.append(min_return_1y_pct / 100.0)  # % 转小数

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            b.c_fd_code,
            b.c_short_name,
            b.c_class1_name,
            b.c_class2_name,
            b.c_manager_name,
            b.c_company_name,
            n.c_nav,
            n.c_ret_1y,
            n.c_ret_ytd,
            n.c_trade_date
        FROM tb_fd_basic_info b
        JOIN (
            SELECT c_fd_code, c_nav, c_ret_1y, c_ret_ytd, c_trade_date,
                   ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_trade_date DESC) AS rn
            FROM tb_fd_nav_daily
        ) n ON b.c_fd_code = n.c_fd_code AND n.rn = 1
        {size_join}
        WHERE {where_clause}
        ORDER BY n.c_ret_1y DESC
        LIMIT {limit}
    """

    print(f"[FundFilter] 筛选条件: type={fund_type}, min_size={min_size_billion}亿, "
          f"max_size={max_size_billion}亿, min_ret1y={min_return_1y_pct}%")

    try:
        rows = execute_query(sql, params=tuple(params), readonly=True)
    except Exception as e:
        return f"筛选查询失败：{type(e).__name__}: {e}"

    if not rows:
        return "未找到符合条件的基金，建议放宽筛选条件。"

    def default_serializer(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return str(obj)
        return str(obj)

    result_str = json.dumps(rows, ensure_ascii=False, default=default_serializer, indent=2)
    return f"筛选到 {len(rows)} 支基金：\n{result_str}"
