"""
get_table_schema 工具实现：读取 templates/table_specs/{table}.md 返回字段说明
"""
import os

_SPECS_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "table_specs")

VALID_TABLES = {
    "tb_fd_basic_info",
    "tb_fd_category",
    "tb_fd_nav_daily",
    "tb_fd_asset_allocation",
    "tb_fd_portfolio_stk",
    "tb_fd_portfolio_bd",
    "tb_fd_perform_abs",
    "tb_dict_params",
    "tb_fd_tag_asset_eq",
}


def get_table_schema(tables: list) -> str:
    """
    读取指定表的详细结构说明。
    返回拼接后的 Markdown 字符串，多表用分隔线隔开。
    """
    results = []
    for table in tables:
        table = table.strip()
        if table not in VALID_TABLES:
            results.append(
                f"## ❌ 表 '{table}' 不存在\n"
                f"可用表名：{', '.join(sorted(VALID_TABLES))}"
            )
            continue
        spec_path = os.path.join(_SPECS_DIR, f"{table}.md")
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                results.append(f.read())
        except FileNotFoundError:
            results.append(f"## ❌ 找不到 {table} 的 spec 文件")

    return "\n\n---\n\n".join(results)
