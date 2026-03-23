"""
本地开发数据库 CSV 导入脚本
用法：cd data && python import.py
前提：
  1. Docker MySQL 已启动：docker start dev-mysql
  2. fund_platform 库已执行 schema_mysql.sql 建表
  3. pip install pandas mysql-connector-python
"""
import os
import sys
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ── 连接配置 ──────────────────────────────────────────────────────────────────
DB_CONFIG = dict(
    host="127.0.0.1", port=3306,
    user="root", password="dev",
    database="fund_platform",
    allow_local_infile=True,
    charset="utf8mb4",
)

# ── 每张表的配置 ───────────────────────────────────────────────────────────────
# date_cols: CSV 中可能出现空字符串的 DATE 列 → 空串转 None
# int_cols:  TINYINT/BIGINT 列 → 空串转 None
# decimal_cols: DECIMAL 列名列表 → 空串转 None

TABLES = [
    {
        "csv": "tb_fd_basic_info.csv",
        "table": "tb_fd_basic_info",
        "date_cols": ["c_estabdate", "c_terminate_date", "c_transform_date"],
        "decimal_cols": ["c_min_hold_period"],
        "int_cols": [],
    },
    {
        "csv": "tb_fd_category.csv",
        "table": "tb_fd_category",
        "date_cols": ["c_report_date"],
        "decimal_cols": [],
        "int_cols": [],
    },
    {
        "csv": "tb_fd_nav_daily.csv",
        "table": "tb_fd_nav_daily",
        "date_cols": ["c_trade_date"],
        "decimal_cols": ["c_nav", "c_nav_acc", "c_nav_adj", "c_nav_adj_pre",
                         "c_ret_tw", "c_ret_tm", "c_ret_adj_estab", "c_ret_estab",
                         "c_ret_ann", "c_ret_1w", "c_ret_1m", "c_ret_3m", "c_ret_6m",
                         "c_ret_1y", "c_ret_2y", "c_ret_3y", "c_ret_4y", "c_ret_5y",
                         "c_ret_ytd", "c_ret_ly", "c_ret_2ya", "c_ret_3ya", "c_ret_4ya",
                         "c_ret_5ya", "c_log_ret_adj", "c_ret_1d", "c_ret_1d_raw"],
        "int_cols": ["c_is_predict", "c_is_trade"],
    },
    {
        "csv": "tb_fd_asset_allocation.csv",
        "table": "tb_fd_asset_allocation",
        "date_cols": ["c_report_date", "c_notice_date"],
        "decimal_cols": [],  # 用 auto_decimal=True
        "int_cols": ["c_is_stat", "c_is_sum", "c_inner_code"],
        "auto_decimal": True,  # 所有 _mv / _ratio / c_fund_ 前缀列
    },
    {
        "csv": "tb_fd_portfolio_stk.csv",
        "table": "tb_fd_portfolio_stk",
        "date_cols": ["c_report_date", "c_notice_date"],
        "decimal_cols": ["c_hold_value", "c_hold_share", "c_nav_ratio"],
        "int_cols": ["c_is_stat", "c_inner_code"],
    },
    {
        "csv": "tb_fd_portfolio_bd.csv",
        "table": "tb_fd_portfolio_bd",
        "date_cols": ["c_report_date", "c_notice_date"],
        "decimal_cols": ["c_hold_num", "c_hold_value", "c_nav_ratio"],
        "int_cols": ["c_is_stat", "c_bd_inner_code"],
    },
    {
        "csv": "tb_fd_perform_abs.csv",
        "table": "tb_fd_perform_abs",
        "date_cols": ["c_trade_date"],
        "decimal_cols": ["c_period_ret", "c_ann_ret", "c_ann_vol", "c_up_side_vol",
                         "c_down_side_vol", "c_mdd", "c_sharpe", "c_calmar",
                         "c_sortino", "c_skewness", "c_kurtosis", "c_break_ratio"],
        "int_cols": [],
    },
    {
        "csv": "tb_fd_tag_asset_eq.csv",
        "table": "tb_fd_tag_asset_eq",
        "date_cols": ["c_report_date"],
        "decimal_cols": ["c_stk_pos_avg", "c_stk_pos_chg_avg"],
        "int_cols": [],
    },
    {
        "csv": "tb_dict_params.csv",
        "table": "tb_dict_params",
        "date_cols": [],
        "decimal_cols": [],
        "int_cols": [],
    },
    {
        "csv": "tb_stk_industry.csv",
        "table": "tb_stk_industry",
        "date_cols": ["c_trade_date"],
        "decimal_cols": [],
        "int_cols": [],
    },
    {
        "csv": "tb_stk_concept.csv",
        "table": "tb_stk_concept",
        "date_cols": ["c_trade_date"],
        "decimal_cols": [],
        "int_cols": [],
    },
]


def clean_df(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """空字符串转 None（对应 MySQL NULL）"""
    # DATE 列：空串 → None
    for col in cfg.get("date_cols", []):
        if col in df.columns:
            df[col] = df[col].replace("", None).where(df[col].notna(), None)

    # DECIMAL 列：空串 → None（用 pd.to_numeric 转换，errors='coerce' 把非数字变 NaN）
    decimal_cols = list(cfg.get("decimal_cols", []))
    if cfg.get("auto_decimal"):
        decimal_cols += [c for c in df.columns
                         if c.endswith("_mv") or c.endswith("_ratio")
                         or c.startswith("c_fund_")]
    for col in set(decimal_cols):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # INT/BIGINT 列：空串 → None
    for col in cfg.get("int_cols", []):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # pandas NaN → None（mysql-connector 能识别 None 为 NULL）
    df = df.where(pd.notna(df), None)
    return df


def import_table(conn, cfg: dict, data_dir: str):
    csv_path = os.path.join(data_dir, cfg["csv"])
    table = cfg["table"]
    print(f"  导入 {table} ...", end=" ", flush=True)

    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    df = clean_df(df, cfg)

    cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join(cols)
    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]

    cursor = conn.cursor()
    batch = 500
    for i in range(0, len(rows), batch):
        cursor.executemany(sql, rows[i:i+batch])
    conn.commit()
    cursor.close()
    print(f"OK ({len(rows)} 行)")


def main():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    print("连接数据库...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"连接失败: {e}")
        sys.exit(1)

    print("开始导入...")
    for cfg in TABLES:
        try:
            import_table(conn, cfg, data_dir)
        except Exception as e:
            print(f"ERROR: {e}")
            conn.rollback()
            raise

    conn.close()
    print("全部完成。")


if __name__ == "__main__":
    main()
