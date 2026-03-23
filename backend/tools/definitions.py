"""
所有 Function Calling 工具的 JSON Schema 定义
"""

ROUTE_TO_TOOL = {
    "type": "function",
    "function": {
        "name": "route_to",
        "description": "将用户请求路由到合适的 Agent 处理",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_key": {
                    "type": "string",
                    "enum": ["chat", "fund_screen", "data_query", "report"],
                    "description": "目标 Agent 标识：chat=闲聊/知识问答，fund_screen=基金筛选，data_query=数据库查询，report=报告生成",
                },
                "reason": {
                    "type": "string",
                    "description": "路由原因（一句话说明）",
                },
            },
            "required": ["agent_key"],
        },
    },
}

EXECUTE_SQL_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": "在基金数据库中执行 SQL 查询（仅支持 SELECT）。执行前会进行安全校验。",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "要执行的 SELECT SQL 语句，必须严格使用数据库结构中定义的表名和字段名",
                },
                "explanation": {
                    "type": "string",
                    "description": "这条 SQL 查询的目的说明",
                },
            },
            "required": ["sql"],
        },
    },
}

RUN_SCREEN_TEMPLATE_TOOL = {
    "type": "function",
    "function": {
        "name": "run_screen_template",
        "description": "执行基金筛选模板。根据 prompt 中的模板目录选择合适的模板 ID，传入所需参数执行筛选。",
        "parameters": {
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "description": "模板 ID，如 '001'。必须从模板目录中选择。",
                },
                "params": {
                    "type": "object",
                    "description": "模板所需参数，键值对。参数名和取值参考模板目录中的参数说明。",
                },
            },
            "required": ["template_id", "params"],
        },
    },
}

GET_TABLE_SCHEMA_TOOL = {
    "type": "function",
    "function": {
        "name": "get_table_schema",
        "description": "获取指定数据库表的详细结构说明，包括字段清单、枚举值、注意事项和查询示例。在写 SQL 之前必须先调用此工具了解表结构。",
        "parameters": {
            "type": "object",
            "properties": {
                "tables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "需要查看的表名列表，如 ['tb_fd_nav_daily', 'tb_fd_perform_abs']",
                }
            },
            "required": ["tables"],
        },
    },
}

GENERATE_REPORT_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_fund_report",
        "description": "为指定基金生成完整的研究报告，包含基础信息、净值表现、持仓结构和综合评价",
        "parameters": {
            "type": "object",
            "properties": {
                "fund_code": {
                    "type": "string",
                    "description": "基金代码，例如 '000001'",
                },
            },
            "required": ["fund_code"],
        },
    },
}
