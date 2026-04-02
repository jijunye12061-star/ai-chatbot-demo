import pymysql
import requests
from config import DB_CONFIG


def get_connection():
    """获取数据库直连。仅 direct 模式（prod）可用。"""
    if DB_CONFIG["mode"] != "direct":
        raise RuntimeError("get_connection() not available in remote mode, use execute_query()")
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )


def _execute_remote(sql: str, params=None) -> list:
    """通过远程 SQL 服务执行查询"""
    resp = requests.post(
        DB_CONFIG["url"],
        json={"sql": sql, "params": params},
        headers={"Authorization": f"Bearer {DB_CONFIG['token']}"},
        timeout=15,
    )
    if resp.status_code != 200:
        ct = resp.headers.get("content-type", "")
        detail = resp.json().get("detail", resp.text) if ct.startswith("application/json") else resp.text
        raise RuntimeError(f"Remote SQL error ({resp.status_code}): {detail}")
    return resp.json()["rows"]


def execute_query(sql: str, params=None, readonly: bool = False) -> list:
    """执行 SELECT 查询，返回字典列表。dev 走远程服务，prod 走直连。"""
    if DB_CONFIG["mode"] == "remote":
        return _execute_remote(sql, params)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()
