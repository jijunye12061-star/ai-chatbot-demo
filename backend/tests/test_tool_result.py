from tools.tool_result import ToolResult


def test_tool_result_full():
    tr = ToolResult(
        summary="共 10 行，前5条如下：\n| a | b |\n|---|---|\n| 1 | 2 |",
        full_rows=[[1, 2], [3, 4]],
        columns=["a", "b"],
    )
    assert tr.summary.startswith("共 10 行")
    assert tr.full_rows == [[1, 2], [3, 4]]
    assert tr.columns == ["a", "b"]
    assert tr.has_full_data is True


def test_tool_result_no_full_data():
    tr = ToolResult(summary="共 3 行：\n...", full_rows=None, columns=None)
    assert tr.has_full_data is False
