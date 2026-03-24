"""
申万行业曝露度筛选（模板003, python_func）

逻辑：
  1. 最新一期：各基金持有指定申万行业成分股的 nav_ratio 之和（latest_exposure）
  2. 历史双验：最近2期中报/年报（c_style IN '02','04'）的各期曝露度均值（hist_exposure）
  3. 两个阈值均满足 → 按 latest_exposure 降序返回

行业码匹配：
  - 6位一级：LEFT(c_sw_code, 6) IN (...)
  - 9位二级：LEFT(c_sw_code, 9) IN (...)
  - 12位三级：c_sw_code IN (...)
  支持混合长度，多组条件用 OR 连接

去重策略（同 concept_exposure.py）：
  同一 (c_fd_code, c_report_date, c_stk_code) 可能出现多个 c_style（如 04=年报, 06=四季报）
  优先级：04 > 06 > 其他，PARTITION BY (c_fd_code, c_report_date, c_stk_code)

注意（dev 数据局限）：
  tb_stk_industry 只有 2025-09-30 和 2025-12-31 两个截面；
  中报 2025-06-30 无行业数据，hist 查询在 dev 结果稀少属正常，生产不受影响
"""
from collections import defaultdict

from db.connection import execute_query
from db.safety import validate_sql

_STYLE_PRIO = "CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END"


def industry_exposure_filter(
    sw_codes: list,
    min_latest_exposure: float = 5.0,
    min_hist_exposure: float = 5.0,
    fund_category_code: str = None,
    limit: int = 50,
) -> list:
    """
    申万行业曝露度筛选。

    参数（经 _validate_params 校验后传入）：
    - sw_codes: 申万行业代码列表（支持6/9/12位混合，如 ['029023', '029011009']）
    - min_latest_exposure: 最新一期曝露度下限（%），默认5
    - min_hist_exposure: 近2期中报/年报均值曝露度下限（%），默认5
    - fund_category_code: 基金一级分类代码（可选），如 '001'=权益基金
    - limit: 返回条数，默认50
    """
    # ── Step 1: 关键时间点 ──────────────────────────────────────────────────────
    latest_date = _get_latest_portfolio_date()
    hist_dates = _get_hist_period_dates(n=2)

    # ── Step 2: latest_exposure ─────────────────────────────────────────────────
    latest_map = _query_latest_exposure(
        sw_codes, latest_date, min_latest_exposure, fund_category_code
    )
    if not latest_map:
        return []

    # ── Step 3: hist_exposure（每期分别求和，Python 侧计算均值）──────────────────
    hist_map = _query_hist_exposure(sw_codes, hist_dates, min_hist_exposure)
    if not hist_map:
        common_funds = set(latest_map.keys())
    else:
        common_funds = set(latest_map) & set(hist_map)

    if not common_funds:
        return []

    # ── Step 4: 基本信息 + 拼装 ─────────────────────────────────────────────────
    info_map = _query_fund_info(common_funds)

    results = []
    for fd in common_funds:
        info = info_map.get(fd, {})
        row = {
            "c_fd_code": fd,
            "c_short_name": info.get("c_short_name"),
            "c_type1_name": info.get("c_type1_name"),
            "c_type2_name": info.get("c_type2_name"),
            "latest_exposure": round(latest_map[fd], 2),
        }
        if fd in hist_map:
            row["hist_exposure"] = round(hist_map[fd], 2)
        results.append(row)

    results.sort(key=lambda x: x["latest_exposure"], reverse=True)
    return results[:limit]


# ── 辅助函数 ────────────────────────────────────────────────────────────────────

def _get_latest_portfolio_date() -> str:
    rows = execute_query(
        "SELECT MAX(c_report_date) AS d FROM tb_fd_portfolio_stk", readonly=True
    )
    d = rows[0]["d"]
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)


def _get_hist_period_dates(n: int = 2) -> list:
    """取最近 n 期中报/年报的报告日期（字符串列表）。"""
    rows = execute_query(
        "SELECT DISTINCT c_report_date FROM tb_fd_portfolio_stk "
        "WHERE c_style IN ('02', '04') ORDER BY c_report_date DESC LIMIT %s",
        params=(n,),
        readonly=True,
    )
    return [
        r["c_report_date"].strftime("%Y-%m-%d") if hasattr(r["c_report_date"], "strftime")
        else str(r["c_report_date"])
        for r in rows
    ]


def _build_sw_condition(sw_codes: list, alias: str = "si") -> tuple[str, list]:
    """
    按行业码长度分组，构建 SW 行业匹配条件。
    alias: 表别名（默认 si，hist 查询中用 si2）
    返回 (sql_fragment, params_list)
    """
    groups: dict[int, list] = {}
    for code in sw_codes:
        length = len(code)
        if length not in (6, 9, 12):
            raise ValueError(f"申万行业代码 '{code}' 长度 {length} 无效，应为6/9/12位")
        groups.setdefault(length, []).append(code)

    parts = []
    params = []
    for length in sorted(groups):
        codes = groups[length]
        ph = ", ".join(["%s"] * len(codes))
        if length == 12:
            parts.append(f"{alias}.c_sw_code IN ({ph})")
        else:
            parts.append(f"LEFT({alias}.c_sw_code, {length}) IN ({ph})")
        params.extend(codes)
    return "(" + " OR ".join(parts) + ")", params


def _dedup_subquery(report_date_placeholder: str, style_filter: str = "") -> str:
    return (
        f"SELECT c_fd_code, c_report_date, c_stk_code, "
        f"MIN({_STYLE_PRIO}) AS best_prio "
        f"FROM tb_fd_portfolio_stk "
        f"WHERE {report_date_placeholder} {style_filter} "
        f"GROUP BY c_fd_code, c_report_date, c_stk_code"
    )


def _query_latest_exposure(
    sw_codes: list,
    latest_date: str,
    min_exposure: float,
    fund_category_code: str = None,
) -> dict:
    sw_cond, sw_params = _build_sw_condition(sw_codes)
    cat_filter = "AND cat.c_type1_code = %s" if fund_category_code else ""

    sql = f"""
    SELECT p.c_fd_code, SUM(p.c_nav_ratio) AS latest_exposure
    FROM ({_dedup_subquery('c_report_date = %s')}) best
    JOIN tb_fd_portfolio_stk p
      ON p.c_fd_code = best.c_fd_code
      AND p.c_stk_code = best.c_stk_code
      AND p.c_report_date = best.c_report_date
      AND {_STYLE_PRIO} = best.best_prio
    JOIN tb_stk_industry si
      ON p.c_stk_code = si.c_stk_code
      AND p.c_report_date = si.c_trade_date
      AND {sw_cond}
    LEFT JOIN (
        SELECT c_fd_code, c_type1_code,
               ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
        FROM tb_fd_category
    ) cat ON p.c_fd_code = cat.c_fd_code AND cat.rn = 1
    WHERE p.c_report_date = %s
    {cat_filter}
    GROUP BY p.c_fd_code
    HAVING SUM(p.c_nav_ratio) >= %s
    """

    params = [latest_date, *sw_params, latest_date]
    if fund_category_code:
        params.append(fund_category_code)
    params.append(min_exposure)

    ok, checked_sql = validate_sql(sql)
    if not ok:
        raise ValueError(f"SQL 安全校验失败: {checked_sql}")
    rows = execute_query(checked_sql, params=tuple(params), readonly=True)
    return {r["c_fd_code"]: float(r["latest_exposure"]) for r in rows}


def _query_hist_exposure(
    sw_codes: list,
    hist_dates: list,
    min_exposure: float,
) -> dict:
    """
    返回 {c_fd_code: hist_exposure_avg}，均值 >= min_exposure 的基金。
    按每期分别求和，Python 侧计算跨期均值。
    """
    if not hist_dates:
        return {}

    sw_cond, sw_params = _build_sw_condition(sw_codes, alias="si2")
    dates_ph = ", ".join(["%s"] * len(hist_dates))

    sql = f"""
    SELECT p2.c_fd_code, p2.c_report_date, SUM(p2.c_nav_ratio) AS exposure
    FROM ({_dedup_subquery(f'c_report_date IN ({dates_ph})', "AND c_style IN ('02', '04')")}) best2
    JOIN tb_fd_portfolio_stk p2
      ON p2.c_fd_code = best2.c_fd_code
      AND p2.c_stk_code = best2.c_stk_code
      AND p2.c_report_date = best2.c_report_date
      AND {_STYLE_PRIO} = best2.best_prio
    JOIN tb_stk_industry si2
      ON p2.c_stk_code = si2.c_stk_code
      AND p2.c_report_date = si2.c_trade_date
      AND {sw_cond}
    WHERE p2.c_style IN ('02', '04')
    GROUP BY p2.c_fd_code, p2.c_report_date
    """

    params = (*hist_dates, *sw_params)
    ok, checked_sql = validate_sql(sql)
    if not ok:
        raise ValueError(f"SQL 安全校验失败: {checked_sql}")
    rows = execute_query(checked_sql, params=params, readonly=True)

    acc = defaultdict(lambda: [0.0, 0])
    for r in rows:
        acc[r["c_fd_code"]][0] += float(r["exposure"])
        acc[r["c_fd_code"]][1] += 1

    return {
        fd: total / cnt
        for fd, (total, cnt) in acc.items()
        if total / cnt >= min_exposure
    }


def _query_fund_info(fund_codes: set) -> dict:
    ph = ", ".join(["%s"] * len(fund_codes))
    rows = execute_query(
        f"""
        SELECT b.c_fd_code, b.c_short_name, cat.c_type1_name, cat.c_type2_name
        FROM tb_fd_basic_info b
        LEFT JOIN (
            SELECT c_fd_code, c_type1_name, c_type2_name,
                   ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
            FROM tb_fd_category
        ) cat ON b.c_fd_code = cat.c_fd_code AND cat.rn = 1
        WHERE b.c_fd_code IN ({ph})
        """,
        params=tuple(fund_codes),
        readonly=True,
    )
    return {r["c_fd_code"]: r for r in rows}
