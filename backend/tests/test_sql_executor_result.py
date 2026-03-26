"""
测试 execute_sql 的 ToolResult 返回格式（mock DB，无需真实连接）。
"""
from unittest.mock import patch
from tools.sql_executor import execute_sql
from tools.tool_result import ToolResult

MOCK_ROWS_SMALL = [{"c_fd_code": "000001", "c_nav": 1.5}] * 3   # 3行 → 无 full_rows

MOCK_ROWS_LARGE = [{"c_fd_code": f"{i:06d}", "c_nav": 1.0 + i * 0.01} for i in range(10)]  # 10行 → 有 full_rows

def test_small_result_no_full_rows():
    with patch("tools.sql_executor.validate_sql", return_value=(True, "SELECT 1")), \
         patch("tools.sql_executor.execute_query", return_value=MOCK_ROWS_SMALL):
        result = execute_sql("SELECT 1")
    assert isinstance(result, ToolResult)
    assert result.full_rows is None
    assert "3 行" in result.summary

def test_large_result_has_full_rows():
    with patch("tools.sql_executor.validate_sql", return_value=(True, "SELECT 1")), \
         patch("tools.sql_executor.execute_query", return_value=MOCK_ROWS_LARGE):
        result = execute_sql("SELECT 1")
    assert isinstance(result, ToolResult)
    assert result.full_rows is not None
    assert len(result.full_rows) == len(MOCK_ROWS_LARGE)
    assert isinstance(result.full_rows[0], list)
    assert len(result.columns) > 0
    assert "10 行" in result.summary
    # summary 只含前5条
    assert result.summary.count("000001") <= 5

def test_sql_validation_failure_returns_tool_result():
    with patch("tools.sql_executor.validate_sql", return_value=(False, "危险操作")):
        result = execute_sql("DROP TABLE foo")
    assert isinstance(result, ToolResult)
    assert result.full_rows is None
    assert "安全校验" in result.summary

def test_empty_result():
    with patch("tools.sql_executor.validate_sql", return_value=(True, "SELECT 1")), \
         patch("tools.sql_executor.execute_query", return_value=[]):
        result = execute_sql("SELECT 1")
    assert isinstance(result, ToolResult)
    assert result.full_rows is None
