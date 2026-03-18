"""
SQL 安全校验单元测试（无需 DB / LLM）
"""
import pytest
from db.safety import validate_sql


# ── 应被拒绝的 SQL ──────────────────────────────────────────────────────────────

def test_reject_delete():
    ok, msg = validate_sql("DELETE FROM tb_fd_basic_info WHERE c_fd_code='000001'")
    assert not ok
    assert "SELECT" in msg or "DML" in msg or "DELETE" in msg or "未知" in msg


def test_reject_update():
    ok, msg = validate_sql("UPDATE tb_fd_nav_daily SET c_nav=1.5 WHERE c_fd_code='000001'")
    assert not ok


def test_reject_insert():
    ok, msg = validate_sql("INSERT INTO tb_fd_basic_info (c_fd_code) VALUES ('999999')")
    assert not ok


def test_reject_drop():
    ok, msg = validate_sql("DROP TABLE tb_fd_basic_info")
    assert not ok


def test_reject_non_whitelist_table():
    ok, msg = validate_sql("SELECT * FROM secret_table WHERE id=1")
    assert not ok
    assert "白名单" in msg or "secret_table" in msg


def test_reject_semicolon_injection():
    ok, msg = validate_sql(
        "SELECT * FROM tb_fd_basic_info WHERE c_fd_code='000001'; DROP TABLE tb_fd_basic_info"
    )
    assert not ok  # 无论是被危险关键词检测还是分号检测拦截，都应拒绝


def test_reject_deep_subquery():
    ok, msg = validate_sql(
        "SELECT * FROM tb_fd_basic_info WHERE c_fd_code IN "
        "(SELECT c_fd_code FROM tb_fd_nav_daily WHERE c_nav IN "
        "(SELECT c_nav FROM tb_fd_nav_daily WHERE c_fd_code IN "
        "(SELECT c_fd_code FROM tb_fd_basic_info)))"
    )
    assert not ok
    assert "子查询" in msg or "嵌套" in msg


def test_reject_comment_injection():
    # 注释注入后尝试执行 DROP：去注释后残留 DROP 关键词，应被危险关键词检测拦截
    ok, msg = validate_sql(
        "SELECT * FROM tb_fd_basic_info -- comment\nDROP TABLE tb_fd_basic_info"
    )
    assert not ok
    assert "DROP" in msg or "危险" in msg


# ── 应被允许并处理的 SQL ──────────────────────────────────────────────────────────

def test_allow_valid_select_with_limit():
    ok, sql = validate_sql(
        "SELECT c_fd_code, c_short_name FROM tb_fd_basic_info "
        "WHERE c_fd_code='000001' LIMIT 10"
    )
    assert ok
    assert "LIMIT" in sql.upper()


def test_inject_limit_when_missing():
    ok, sql = validate_sql(
        "SELECT * FROM tb_fd_nav_daily WHERE c_fd_code='000001'"
    )
    assert ok
    assert "LIMIT" in sql.upper()


def test_allow_join_whitelist_tables():
    ok, sql = validate_sql(
        "SELECT b.c_short_name, n.c_nav "
        "FROM tb_fd_basic_info b "
        "JOIN tb_fd_nav_daily n ON b.c_fd_code = n.c_fd_code "
        "WHERE b.c_fd_code='000001' "
        "ORDER BY n.c_trade_date DESC LIMIT 5"
    )
    assert ok


def test_allow_all_whitelist_tables():
    allowed = [
        "tb_fd_basic_info",
        "tb_fd_category",
        "tb_fd_nav_daily",
        "tb_fd_asset_allocation",
        "tb_fd_portfolio_bd",
        "tb_fd_portfolio_stk",
        "tb_fd_perform_abs",
        "tb_dict_params",
        "tb_fd_tag_asset_eq",
    ]
    for table in allowed:
        ok, sql = validate_sql(f"SELECT * FROM {table} LIMIT 1")
        assert ok, f"白名单表 {table} 被错误拒绝：{sql}"


def test_strip_trailing_semicolon():
    ok, sql = validate_sql(
        "SELECT c_fd_code FROM tb_fd_basic_info WHERE c_fd_code='000001';"
    )
    assert ok
    assert not sql.strip().endswith(";")


def test_subquery_depth_2_allowed():
    ok, sql = validate_sql(
        "SELECT * FROM tb_fd_portfolio_stk "
        "WHERE c_fd_code IN ("
        "  SELECT c_fd_code FROM tb_fd_basic_info WHERE c_class1_name='股票型'"
        ") LIMIT 10"
    )
    assert ok
