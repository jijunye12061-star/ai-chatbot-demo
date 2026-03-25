"""
所有 Function Calling 工具的 JSON Schema 定义
"""

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

GET_DIMENSION_LIST_TOOL = {
    "type": "function",
    "function": {
        "name": "get_dimension_list",
        "description": "获取概念板块或申万行业分类的全量码+名称列表，供基金筛选时选择匹配的分类码。返回 JSON 数组，每条包含 code/name/parent_code/remark。",
        "parameters": {
            "type": "object",
            "properties": {
                "dim_type": {
                    "type": "string",
                    "description": "维度类型名称，如 '概念板块' 或 '申万行业分类'",
                }
            },
            "required": ["dim_type"],
        },
    },
}

GET_SCREEN_GUIDE_TOOL = {
    "type": "function",
    "function": {
        "name": "get_screen_guide",
        "description": "获取基金筛选场景的 SQL 写法知识文档。筛选前必须先调用此工具了解正确的 SQL 模式。",
        "parameters": {
            "type": "object",
            "properties": {
                "scenarios": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "场景名称列表，可选值：concept_exposure（概念筛选）、"
                        "industry_exposure（行业筛选）、performance_filter（业绩筛选）、"
                        "tag_equity（权益标签）、tag_fixed_income（固收+标签）、"
                        "tag_mixed（混合标签）"
                    ),
                }
            },
            "required": ["scenarios"],
        },
    },
}

ASK_REPORT_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "ask_report_agent",
        "description": "委托报告 Agent 生成指定基金的完整研究报告。只在用户明确要求生成报告时调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "fund_code": {
                    "type": "string",
                    "description": "基金代码，如 '000001'",
                }
            },
            "required": ["fund_code"],
        },
    },
}
