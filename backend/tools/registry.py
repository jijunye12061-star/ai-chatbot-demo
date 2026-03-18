"""
工具注册表：维护 tool_name → {schema, func} 的映射
"""
from tools.definitions import (
    ROUTE_TO_TOOL,
    EXECUTE_SQL_TOOL,
    FILTER_FUNDS_TOOL,
    GENERATE_REPORT_TOOL,
    GET_TABLE_SCHEMA_TOOL,
)

TOOL_REGISTRY: dict = {}


def register_tool(schema: dict, func):
    """注册一个工具"""
    name = schema["function"]["name"]
    TOOL_REGISTRY[name] = {"schema": schema, "func": func}


def _lazy_register():
    """延迟注册，避免循环导入"""
    if TOOL_REGISTRY:
        return

    # schema reader
    from tools.schema_reader import get_table_schema
    register_tool(GET_TABLE_SCHEMA_TOOL, get_table_schema)

    # sql executor
    from tools.sql_executor import execute_sql
    register_tool(EXECUTE_SQL_TOOL, execute_sql)

    # fund filter
    from tools.fund_filter import filter_funds
    register_tool(FILTER_FUNDS_TOOL, filter_funds)

    # report generator
    from tools.report_gen import generate_fund_report
    register_tool(GENERATE_REPORT_TOOL, generate_fund_report)


def get_tool_schemas(names: list) -> list:
    _lazy_register()
    return [TOOL_REGISTRY[n]["schema"] for n in names if n in TOOL_REGISTRY]


def get_tool_func(name: str):
    _lazy_register()
    entry = TOOL_REGISTRY.get(name)
    return entry["func"] if entry else None
