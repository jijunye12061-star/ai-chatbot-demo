import pymysql
from config import DB_CONFIG

# 只读账号配置（AI 生成 SQL 专用）
_RO_CONFIG = {**DB_CONFIG, "user": "readonly", "password": "readonly"}


def get_connection(readonly: bool = False):
    """获取数据库连接。readonly=True 使用只读账号（AI SQL 执行专用）"""
    cfg = _RO_CONFIG if readonly else DB_CONFIG
    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )


def execute_query(sql: str, params=None, readonly: bool = False) -> list:
    """执行 SELECT 查询，返回字典列表。readonly=True 时先设置执行超时。"""
    conn = get_connection(readonly=readonly)
    try:
        with conn.cursor() as cursor:
            if readonly:
                cursor.execute("SET SESSION MAX_EXECUTION_TIME=5000")
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()
