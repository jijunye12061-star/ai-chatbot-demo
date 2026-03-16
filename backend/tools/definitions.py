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

FILTER_FUNDS_TOOL = {
    "type": "function",
    "function": {
        "name": "filter_funds",
        "description": "按条件筛选基金，支持按类型、规模、收益率等条件过滤",
        "parameters": {
            "type": "object",
            "properties": {
                "fund_type": {
                    "type": "string",
                    "description": "基金类型关键词，例如：股票、债券、混合、货币、指数",
                },
                "min_size_billion": {
                    "type": "number",
                    "description": "最小规模（亿元），例如 10 表示规模不低于 10 亿元",
                },
                "max_size_billion": {
                    "type": "number",
                    "description": "最大规模（亿元）",
                },
                "min_return_1y_pct": {
                    "type": "number",
                    "description": "最低近一年收益率（百分比），例如 10 表示近一年收益率不低于 10%",
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量上限，默认 20",
                },
            },
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
