"""
模型展示页面的数据查询服务（收益率曲线、基金净值历史等）
注意：收益率曲线数据来自 tb_fd_nav_daily，使用基金代码模拟曲线，
      如有专门的国债收益率表则替换对应 SQL 即可。
"""
from db.connection import execute_query
from utils.serializers import serialize_row


def get_yield_curve_data(trade_date: str = None) -> dict:
    """
    获取收益率曲线数据。
    当前用 tb_fd_nav_daily 中各期限基金的净值增长率近似模拟。
    实际生产中应替换为真实的国债收益率表。
    返回格式供前端直接使用。
    """
    # 如未指定日期，取最新交易日
    if not trade_date:
        rows = execute_query(
            "SELECT MAX(c_trade_date) AS latest FROM tb_fd_nav_daily",
            readonly=False,
        )
        latest = rows[0]["latest"] if rows and rows[0]["latest"] else None
        trade_date = str(latest) if latest else None

    if not trade_date:
        return {"trade_date": None, "curves": [], "table": []}

    # 查询当日、一月前、一年前的净值数据（用少数样本基金代替国债各期限）
    # 实际项目应替换为真实的国债收益率字段
    sql = """
        SELECT
            c_fd_code,
            c_trade_date,
            c_ret_1y,
            c_ret_6m,
            c_ret_3m,
            c_ret_1m,
            c_ret_1w,
            c_ret_ytd,
            c_nav
        FROM tb_fd_nav_daily
        WHERE c_trade_date = %s
        ORDER BY c_ret_1y DESC
        LIMIT 20
    """
    rows = execute_query(sql, params=(trade_date,), readonly=False)
    rows = [serialize_row(r) for r in rows]

    return {
        "trade_date": trade_date,
        "rows": rows,
        "count": len(rows),
    }


def get_nav_history(fund_code: str, start_date: str = None, end_date: str = None) -> dict:
    """
    获取基金净值历史数据。
    """
    conditions = ["c_fd_code = %s"]
    params = [fund_code]

    if start_date:
        conditions.append("c_trade_date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("c_trade_date <= %s")
        params.append(end_date)

    sql = f"""
        SELECT c_trade_date, c_nav, c_nav_acc, c_nav_adj, c_ret_1d, c_ret_1y
        FROM tb_fd_nav_daily
        WHERE {' AND '.join(conditions)}
        ORDER BY c_trade_date DESC
        LIMIT 365
    """

    rows = execute_query(sql, params=tuple(params), readonly=False)
    rows = [serialize_row(r) for r in rows]

    return {
        "fund_code": fund_code,
        "rows": rows,
        "count": len(rows),
    }
