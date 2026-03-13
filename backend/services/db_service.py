import os
from config import DB_CONFIG, ENV


async def get_connection():
    """获取数据库连接（待实现）

    本地开发: MySQL 8.0 (Docker)
    生产环境: Doris (MySQL 协议兼容)
    """
    # TODO: 使用 aiomysql 或 PyMySQL 连接
    # import aiomysql
    # conn = await aiomysql.connect(**DB_CONFIG)
    # return conn
    raise NotImplementedError(f"DB connection not configured (ENV={ENV})")


async def query_yield_curve(trade_date: str):
    """查询指定日期的收益率曲线数据"""
    # SQL 示例（待接入实际 DB）:
    # SELECT c_trade_date, c_fd_code, c_nav, c_nav_acc
    # FROM tb_fd_nav_daily
    # WHERE c_trade_date = %(trade_date)s
    # ORDER BY c_fd_code
    raise NotImplementedError("待接入数据库")


async def query_nav_history(fd_code: str, start_date: str, end_date: str):
    """查询基金净值历史"""
    raise NotImplementedError("待接入数据库")
