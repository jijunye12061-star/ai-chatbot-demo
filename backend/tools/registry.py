"""
工具注册表：维护 tool_name → {schema, func} 的映射
"""
from tools.definitions import (
    EXECUTE_SQL_TOOL,
    GENERATE_REPORT_TOOL,
    GET_TABLE_SCHEMA_TOOL,
    GET_DIMENSION_LIST_TOOL,
    GET_SCREEN_GUIDE_TOOL,
    ASK_REPORT_AGENT_TOOL,
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

    # report generator
    from tools.report_gen import generate_fund_report
    register_tool(GENERATE_REPORT_TOOL, generate_fund_report)

    # dimension lookup (for fund screener)
    from tools.dimension_lookup import get_dimension_list
    register_tool(GET_DIMENSION_LIST_TOOL, get_dimension_list)

    # screen guide reader (for fund screener)
    from tools.screen_guide_reader import get_screen_guide as _get_screen_guide
    register_tool(GET_SCREEN_GUIDE_TOOL, _get_screen_guide)

    # report agent bridge
    from tools.report_agent_bridge import ask_report_agent as _ask_report_agent
    register_tool(ASK_REPORT_AGENT_TOOL, _ask_report_agent)


def get_tool_schemas(names: list) -> list:
    _lazy_register()
    return [TOOL_REGISTRY[n]["schema"] for n in names if n in TOOL_REGISTRY]


def get_tool_func(name: str):
    _lazy_register()
    entry = TOOL_REGISTRY.get(name)
    return entry["func"] if entry else None
