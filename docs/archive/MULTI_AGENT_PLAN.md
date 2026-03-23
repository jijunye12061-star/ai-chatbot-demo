# 基金研究平台 — 多 Agent AI 问答架构方案

> 版本：v1.0 | 日期：2026-03-16
>
> 本文档定义后端整体架构（含 AI 问答 + 模型展示页面），多 Agent 设计方案，开发任务分解与测试策略。

---

## 一、设计原则

1. **AI 模块是 backend 的子包**，不单独建项目。它是 `services/llm_service.py` 的升级替换，对前端透明。
2. **数据库连接层全局共享**，模型展示页面和 AI 问答共用同一个 `db/` 层。
3. **Prompt 与代码分离**，使用 Markdown 文件管理 prompt，便于非开发人员阅读和修改。
4. **轻量自研编排**，不引入 AgentScope 等外部框架，用 Function Calling 循环 + Python 类实现多 Agent。
5. **解耦开发**，AI 管道可独立于前端通过 CLI/pytest 测试，其他页面后端预留接口但不阻塞 AI 开发。
6. **先硬后软**，SQL 安全先做确定性代码防护，LLM 审查作为后续增强。

---

## 二、Backend 目录结构

```
backend/
├── main.py                     # FastAPI 入口，注册所有 router
├── config.py                   # 全局配置（LLM / 环境 / 其他）
│
├── db/                         # 【公共】数据库连接层（AI + 页面共用）
│   ├── __init__.py
│   ├── connection.py           # get_connection()，基于 APP_ENV 切换 dev/prod
│   ├── config.py               # DB_CONFIG（从 config.py 迁移过来）
│   └── safety.py               # SQL 安全校验（白名单表、只允许 SELECT、强制 LIMIT 等）
│
├── api/                        # FastAPI 路由层
│   ├── chat.py                 # POST /api/chat — AI 问答 SSE 入口
│   ├── models.py               # GET /api/models, GET /api/models/{id}/data — 模型展示页面
│   └── __init__.py
│
├── services/                   # 【公共】业务逻辑层（页面数据查询等）
│   ├── model_data_service.py   # 收益率曲线、资产配置等页面的数据查询
│   └── __init__.py
│
├── agents/                     # 【AI 核心】多 Agent 编排
│   ├── __init__.py
│   ├── base.py                 # BaseAgent 基类
│   ├── orchestrator.py         # 总调度入口：消息 → 路由 → agent → SSE 流
│   ├── router_agent.py         # 意图识别 agent（分流到具体 skill agent）
│   ├── chat_agent.py           # 兜底闲聊 agent（当前 llm_service 的角色）
│   ├── fund_screener_agent.py  # 基金筛选 agent
│   ├── data_query_agent.py     # 查数 agent（SQL 生成 + 执行）
│   └── report_agent.py         # 报告生成 agent
│
├── prompts/                    # 【AI】Prompt 模板（Markdown 格式）
│   ├── router.md               # 路由 agent 的 system prompt
│   ├── chat.md                 # 闲聊 agent
│   ├── fund_screener.md        # 基金筛选
│   ├── data_query.md           # 查数 / SQL 生成
│   ├── sql_reviewer.md         # SQL 安全审查（后续软性防护用）
│   └── report_writer.md        # 报告撰写
│
├── tools/                      # 【AI】Function Calling 工具层
│   ├── __init__.py
│   ├── registry.py             # tool_name → 执行函数 的注册表
│   ├── definitions.py          # 所有 tool 的 JSON Schema 定义
│   ├── fund_filter.py          # 基金筛选执行逻辑
│   ├── sql_executor.py         # SQL 生成 → 安全校验 → 执行 → 返回结果
│   └── report_gen.py           # 报告模板填充 + 分节生成
│
├── templates/                  # 【AI】报告模板 & 数据库元数据
│   ├── fund_report.json        # 基金研究报告模板定义（各节结构）
│   └── db_schema.md            # 数据库表结构说明（给 SQL 生成 agent 看的上下文）
│
├── llm/                        # 【AI】LLM 调用封装
│   ├── __init__.py
│   └── client.py               # 统一 LLM 调用（替代原 llm_service.py），支持流式/非流式
│
└── tests/                      # 测试
    ├── test_router_agent.py
    ├── test_sql_safety.py
    ├── test_orchestrator.py
    └── test_tools.py
```

### 与原结构的对应关系

| 原文件                       | 变更                                                                   |
|---------------------------|----------------------------------------------------------------------|
| `config.py`               | 保留，DB 配置迁移到 `db/config.py`，LLM 配置迁移到 `llm/` 或保留                      |
| `services/llm_service.py` | → 拆分为 `llm/client.py`（底层调用）+ `agents/chat_agent.py`（闲聊逻辑）            |
| `services/db_service.py`  | → 拆分为 `db/connection.py`（连接）+ `services/model_data_service.py`（页面查询） |
| `api/chat.py`             | 保留，改为调用 `orchestrator.run()`                                         |
| `api/models.py`           | 保留，改为调用 `services/model_data_service.py`                             |

---

## 三、核心模块设计

### 3.1 数据库层 `db/`

全局共享，AI 和页面都通过此层访问数据库。

```python
# db/connection.py
import pymysql
from db.config import DB_CONFIG


def get_connection():
    """同步连接，基于 APP_ENV 自动切换 dev(Docker MySQL) / prod(Doris)"""
    return pymysql.connect(**DB_CONFIG, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)


def execute_query(sql: str, params: tuple = None) -> list[dict]:
    """执行 SELECT 查询，返回字典列表"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()
```

```python
# db/safety.py
import sqlparse

ALLOWED_TABLES = ["tb_fd_nav_daily", "tb_fd_info", "tb_yield_curve", ...]  # 白名单
MAX_ROWS = 1000
MAX_EXECUTION_TIME_MS = 5000


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    硬性安全校验：
    1. 只允许 SELECT
    2. 只允许访问白名单表
    3. 强制注入 LIMIT（如缺失）
    返回 (is_safe, sanitized_sql 或 error_message)
    """
    parsed = sqlparse.parse(sql)
    # ... 校验逻辑
```

### 3.2 LLM 客户端 `llm/client.py`

从原 `llm_service.py` 提取出来的纯 LLM 调用层，所有 agent 共用。

```python
# llm/client.py
from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat_completion(messages: list, tools: list = None, stream: bool = True, **kwargs):
    """统一 LLM 调用入口"""
    params = {"model": MODEL, "messages": messages, "stream": stream, **kwargs}
    if tools:
        params["tools"] = tools
    return client.chat.completions.create(**params)


async def stream_chunks(response):
    """将 OpenAI stream response 转为 SSE chunk generator"""
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            yield {"type": "content", "data": delta.content}
        if delta.tool_calls:
            yield {"type": "tool_call", "data": delta.tool_calls}
```

### 3.3 BaseAgent 基类

```python
# agents/base.py
from typing import AsyncGenerator
from llm.client import chat_completion
from tools.registry import TOOL_REGISTRY


class BaseAgent:
    def __init__(self, name: str, prompt_file: str, tools: list[str] = None):
        self.name = name
        self.system_prompt = self._load_prompt(prompt_file)
        self.tool_schemas = [TOOL_REGISTRY[t]["schema"] for t in (tools or [])]
        self.tool_funcs = {t: TOOL_REGISTRY[t]["func"] for t in (tools or [])}

    def _load_prompt(self, filename: str) -> str:
        """从 prompts/ 目录加载 Markdown prompt"""
        with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
            return f.read()

    async def run(self, messages: list) -> AsyncGenerator[str, None]:
        """
        Function Calling 循环：
        1. 调 LLM（带 tools）
        2. 如果返回 tool_call → 执行 tool → 结果塞回 messages → 回到 1
        3. 如果返回纯文本 → yield 文本 chunks → 结束
        """
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        while True:
            response = chat_completion(full_messages, tools=self.tool_schemas or None, stream=False)
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                # 执行 tool，结果追加到 messages
                for tc in choice.message.tool_calls:
                    result = await self._execute_tool(tc.function.name, tc.function.arguments)
                    full_messages.append(choice.message)
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result)
                    })
                continue  # 继续循环
            else:
                # 最终文本回复 — 用流式输出
                response_stream = chat_completion(full_messages, stream=True)
                for chunk in response_stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
                break

    async def _execute_tool(self, tool_name: str, arguments: str) -> str:
        import json
        args = json.loads(arguments)
        func = self.tool_funcs[tool_name]
        return await func(**args) if asyncio.iscoroutinefunction(func) else func(**args)
```

### 3.4 Orchestrator 调度器

```python
# agents/orchestrator.py
from agents.router_agent import RouterAgent
from agents.chat_agent import ChatAgent
from agents.fund_screener_agent import FundScreenerAgent
from agents.data_query_agent import DataQueryAgent
from agents.report_agent import ReportAgent

AGENT_MAP = {
    "chat": ChatAgent(),
    "fund_screen": FundScreenerAgent(),
    "data_query": DataQueryAgent(),
    "report": ReportAgent(),
}

router = RouterAgent()


async def run(message: str, history: list) -> AsyncGenerator[str, None]:
    """
    总调度入口：
    1. RouterAgent 判断意图 → 返回 agent_key
    2. 分发到对应 agent.run()
    3. yield SSE chunks
    """
    messages = history + [{"role": "user", "content": message}]

    # 路由
    intent = await router.classify(messages)
    agent = AGENT_MAP.get(intent, AGENT_MAP["chat"])

    # 执行
    async for chunk in agent.run(messages):
        yield chunk
```

### 3.5 Router Agent（意图识别）

```python
# agents/router_agent.py
class RouterAgent:
    def __init__(self):
        self.system_prompt = self._load_prompt("router.md")

    async def classify(self, messages: list) -> str:
        """
        调用 LLM 做意图分类，返回 agent_key。
        使用 Function Calling 保证返回结构化结果。
        """
        # tool 定义：route_to(agent_key: Literal["chat","fund_screen","data_query","report"])
        # LLM 必须调用此 tool，返回一个明确的 agent_key
        ...
```

对应的 prompt 文件：

```markdown
<!-- prompts/router.md -->

# 路由 Agent

你是基金研究平台的意图路由器。根据用户消息判断应该由哪个 Agent 处理。

## 可选路由

| agent_key    | 适用场景                                       |
|-------------|----------------------------------------------|
| chat         | 通用闲聊、金融知识问答、概念解释                    |
| fund_screen  | 筛选基金（按规模、收益率、类型等条件过滤）            |
| data_query   | 查询具体数据（净值、收益率、持仓等，需要查数据库）     |
| report       | 生成基金研究报告                                  |

## 规则

- 如果用户意图不明确，默认路由到 `chat`
- 如果用户同时有多个意图，选择最主要的那个
- 只返回一个 agent_key，通过调用 route_to 工具
```

### 3.6 SQL 执行流程

```
用户: "帮我查一下000001近一个月的净值"
  → RouterAgent → intent: "data_query"
  → DataQueryAgent.run()
    → LLM 读取 db_schema.md 上下文，生成 SQL
    → LLM 调用 execute_sql tool，传入 SQL
    → tools/sql_executor.py:
        1. db.safety.validate_sql(sql)  → 不通过则返回错误信息给 LLM
        2. 注入 LIMIT 和 MAX_EXECUTION_TIME
        3. 使用只读账号通过 db.connection 执行
        4. 格式化结果返回给 LLM
    → LLM 收到查询结果，组织自然语言回复
    → yield 流式文本
```

### 3.7 报告生成流程

```json
// templates/fund_report.json
{
  "name": "基金研究报告",
  "sections": [
    {
      "id": "basic_info",
      "title": "一、基金基本信息",
      "data_sql": "SELECT fund_code, fund_name, fund_type, setup_date, fund_manager, fund_size FROM tb_fd_info WHERE fund_code = '{fund_code}'",
      "prompt_file": "report_section_basic.md",
      "format": "paragraph",
      "parallel_group": 1
    },
    {
      "id": "investment_strategy",
      "title": "二、投资策略分析",
      "data_sql": "SELECT ... FROM tb_fd_strategy WHERE fund_code = '{fund_code}'",
      "prompt_file": "report_section_strategy.md",
      "format": "paragraph",
      "parallel_group": 1
    },
    {
      "id": "performance",
      "title": "三、业绩表现",
      "data_sql": "SELECT ... FROM tb_fd_nav_daily WHERE ...",
      "prompt_file": "report_section_performance.md",
      "format": "paragraph_with_table",
      "parallel_group": 1
    },
    {
      "id": "summary",
      "title": "四、总结与建议",
      "data_sql": null,
      "prompt_file": "report_section_summary.md",
      "format": "paragraph",
      "parallel_group": 2,
      "depends_on": [
        "basic_info",
        "investment_strategy",
        "performance"
      ]
    }
  ]
}
```

**执行逻辑（ReportAgent）：**

1. 按 `parallel_group` 分组
2. Group 1 的所有 section 并行执行（`asyncio.gather`）：各自 SQL 取数 → 喂给 LLM 生成文字
3. Group 2 等 Group 1 全部完成后执行：将前面所有 section 内容作为上下文，生成总结
4. 拼装完整 Markdown 报告，流式输出给用户

---

## 四、Prompt 管理规范

所有 prompt 放在 `prompts/` 目录下，使用 **Markdown 格式**。

**选择 Markdown 而非 JSON 的理由：**

- 可读性强，非开发人员也能看懂和修改
- 支持富格式（表格、列表、代码块），Prompt 工程中经常用到
- Git diff 友好
- Python 读取就是一行 `open().read()`

**命名规范：** `{agent 或 section 名}.md`

**模板变量：** 使用 Python `str.format()` 或 `string.Template`

```markdown
<!-- prompts/data_query.md -->

# 数据查询 Agent

你是基金研究平台的数据查询助手。用户会问关于基金的各种数据问题，你需要生成 SQL 来查询数据库。

## 数据库结构

{db_schema}

## 规则

- 只生成 SELECT 语句
- 表名和字段名必须严格按照上方数据库结构
- 所有查询必须包含 WHERE 条件，不允许全表扫描
- 结果数据用清晰的表格或文字呈现给用户
```

加载时动态注入变量：

```python
prompt = self._load_prompt("data_query.md")
db_schema = self._load_prompt("../templates/db_schema.md")
final_prompt = prompt.format(db_schema=db_schema)
```

---

## 五、API 层变更

`api/chat.py` 的变更很小——只需把调用目标从 `llm_service` 换成 `orchestrator`：

```python
# api/chat.py（改造后）
from agents.orchestrator import run as agent_run


@router.post("/chat")
async def chat(request: ChatRequest):
    async def event_stream():
        async for chunk in agent_run(request.message, request.history):
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

前端完全不需要改动。SSE 协议和数据格式保持一致。

---

## 六、SQL 安全方案（第一阶段：硬性防护）

全部在代码层实现，不依赖 LLM 判断，确定性保障。

| 防护措施       | 实现位置            | 说明                                                  |
|------------|-----------------|-----------------------------------------------------|
| 只允许 SELECT | `db/safety.py`  | `sqlparse` 解析语句类型，拒绝 DML/DDL                        |
| 只读数据库账号    | Docker MySQL 配置 | `GRANT SELECT ON fund_platform.* TO 'readonly'@'%'` |
| 白名单表       | `db/safety.py`  | 只允许访问 `templates/db_schema.md` 中列出的表                |
| 强制 LIMIT   | `db/safety.py`  | 无 LIMIT 自动追加 `LIMIT 1000`                           |
| 执行超时       | `db/safety.py`  | SQL 前注入 `SET MAX_EXECUTION_TIME=5000`（5 秒）          |
| 禁止子查询嵌套过深  | `db/safety.py`  | 解析 AST，子查询层数 ≤ 2                                    |

**后续软性防护（不在第一阶段实现）：**

- SQL Reviewer Agent：LLM 二次审查生成的 SQL
- 敏感字段脱敏：如持有人信息等
- 查询日志审计

---

## 七、本地开发环境

沿用现有 Docker MySQL 方案，增加只读账号：

```bash
# 启动（已有）
docker start dev-mysql

# 新增只读账号（一次性执行）
docker exec -i dev-mysql mysql -uroot -pdev -e "
  CREATE USER IF NOT EXISTS 'readonly'@'%' IDENTIFIED BY 'readonly';
  GRANT SELECT ON fund_platform.* TO 'readonly'@'%';
  FLUSH PRIVILEGES;
"
```

`db/config.py` 中维护两套连接信息：

```python
# 页面数据查询用 root（后续也可改为 readonly）
DB_CONFIG_RW = {"user": "root", "password": "dev", ...}

# AI SQL 执行专用只读账号
DB_CONFIG_RO = {"user": "readonly", "password": "readonly", ...}
```

---

## 八、开发任务分解

### Phase A：骨架搭建（可独立测试，不动前端）

> 目标：最小链路跑通——用户消息 → Router → ChatAgent → 流式回复

| #  | 任务                 | 产出文件                                                                            | 验证方式                                                    |
|----|--------------------|---------------------------------------------------------------------------------|---------------------------------------------------------|
| A1 | 搭建 `db/` 公共层       | `db/connection.py`, `db/config.py`, `db/safety.py`                              | `pytest test_sql_safety.py`（纯单元测试，validate_sql 各种 case） |
| A2 | 搭建 `llm/client.py` | `llm/client.py`                                                                 | CLI 脚本直接调用，确认能拿到 DeepSeek-V3 的回复                        |
| A3 | BaseAgent 基类       | `agents/base.py`                                                                | 无需单独测试                                                  |
| A4 | ChatAgent（兜底）      | `agents/chat_agent.py`, `prompts/chat.md`                                       | CLI 测试：`python -m agents.chat_agent "你好"`               |
| A5 | RouterAgent        | `agents/router_agent.py`, `prompts/router.md`, `tools/definitions.py`(route_to) | CLI 测试：输入不同问题，检查路由结果                                    |
| A6 | Orchestrator       | `agents/orchestrator.py`                                                        | CLI 测试：完整链路 message → route → agent → 输出                |
| A7 | 接入 API 层           | 修改 `api/chat.py`                                                                | `curl` 或 Postman 测试 SSE 流                               |
| A8 | 前端验证               | 无需改前端代码                                                                         | 打开聊天页面，正常对话即通过                                          |

**Phase A 完成标志：** 通过前端聊天，体验与改造前一致（因为所有消息都路由到 ChatAgent），但内部已经走多 Agent 架构。

### Phase B：数据查询能力

| #  | 任务                   | 产出文件                                                  | 验证方式                                    |
|----|----------------------|-------------------------------------------------------|-----------------------------------------|
| B1 | 编写 `db_schema.md`    | `templates/db_schema.md`                              | 人工 review                               |
| B2 | SQL 安全校验完善           | `db/safety.py` 完善                                     | `pytest test_sql_safety.py` 补充边界 case   |
| B3 | sql_executor tool    | `tools/sql_executor.py`, `tools/definitions.py` 补充    | 单元测试：构造 SQL → validate → execute → 返回结果 |
| B4 | DataQueryAgent       | `agents/data_query_agent.py`, `prompts/data_query.md` | CLI 测试："查一下000001近一个月的净值"               |
| B5 | Router 支持 data_query | 更新 `prompts/router.md`                                | CLI 测试：确认查数问题路由正确                       |
| B6 | 集成测试                 | —                                                     | 前端对话测试                                  |

### Phase C：基金筛选能力

| #  | 任务                | 产出文件                                                        | 验证方式                   |
|----|-------------------|-------------------------------------------------------------|------------------------|
| C1 | fund_filter tool  | `tools/fund_filter.py`, `tools/definitions.py` 补充           | 单元测试                   |
| C2 | FundScreenerAgent | `agents/fund_screener_agent.py`, `prompts/fund_screener.md` | CLI："帮我筛选规模大于10亿的债券基金" |
| C3 | 集成测试              | —                                                           | 前端对话测试                 |

### Phase D：报告生成能力

| #  | 任务                    | 产出文件                                                 | 验证方式                    |
|----|-----------------------|------------------------------------------------------|-------------------------|
| D1 | 报告模板定义                | `templates/fund_report.json`, 各 section prompt       | 人工 review               |
| D2 | report_gen tool（并行逻辑） | `tools/report_gen.py`                                | 单元测试：mock 数据生成各 section |
| D3 | ReportAgent           | `agents/report_agent.py`, `prompts/report_writer.md` | CLI："帮我生成000001的研究报告"   |
| D4 | 集成测试                  | —                                                    | 前端查看完整报告输出              |

### Phase E：页面数据接入（可与 B/C/D 并行）

| #  | 任务                               | 说明                                   |
|----|----------------------------------|--------------------------------------|
| E1 | `services/model_data_service.py` | 收益率曲线页面的数据查询，调用 `db/connection.py`   |
| E2 | `api/models.py` 接真实数据            | GET /api/models/{id}/data 返回真实 DB 数据 |
| E3 | 前端 YieldCurve.vue 改接 API         | 去掉 mock 数据                           |

---

## 九、测试策略

### 9.1 独立测试 AI 管道（不启动 FastAPI、不启动前端）

每个 agent 和 tool 都可以通过 CLI 脚本独立测试：

```bash
# 测试 LLM 连通性
python -c "from llm.client import chat_completion; r = chat_completion([{'role':'user','content':'hi'}], stream=False); print(r.choices[0].message.content)"

# 测试单个 agent
python -m agents.chat_agent "你好，介绍一下自己"
python -m agents.router_agent "帮我筛选规模大于10亿的债券基金"
python -m agents.data_query_agent "查一下000001最近一周的净值"

# 测试完整链路
python -m agents.orchestrator "帮我查一下000001近一个月的净值"
```

实现方式：每个 agent 文件底部加 `if __name__ == "__main__"` 块：

```python
# agents/chat_agent.py 末尾
if __name__ == "__main__":
    import sys, asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "你好"
    agent = ChatAgent()


    async def main():
        async for chunk in agent.run([{"role": "user", "content": query}]):
            print(chunk, end="", flush=True)
        print()


    asyncio.run(main())
```

### 9.2 单元测试（pytest）

```bash
cd backend
pytest tests/ -v

# 重点测试项
pytest tests/test_sql_safety.py     # SQL 校验：各种注入和违规 case
pytest tests/test_router_agent.py   # 路由准确性：10+ 条测试用例覆盖各意图
pytest tests/test_tools.py          # tool 执行逻辑（mock DB）
```

SQL Safety 测试用例示例：

```python
# tests/test_sql_safety.py
def test_reject_delete():
    ok, msg = validate_sql("DELETE FROM tb_fd_info")
    assert not ok


def test_reject_non_whitelist_table():
    ok, msg = validate_sql("SELECT * FROM secret_table")
    assert not ok


def test_inject_limit():
    ok, sql = validate_sql("SELECT * FROM tb_fd_info WHERE fund_code='000001'")
    assert ok
    assert "LIMIT" in sql


def test_allow_valid_select():
    ok, sql = validate_sql("SELECT fund_code, fund_name FROM tb_fd_info WHERE fund_code='000001' LIMIT 10")
    assert ok
```

### 9.3 集成测试（启动 FastAPI，不启动前端）

```bash
# 终端 1：启动后端
cd backend && uvicorn main:app --reload --port 8000

# 终端 2：curl 测试 SSE
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我查一下000001的最新净值", "history": []}' \
  --no-buffer
```

### 9.4 端到端测试（前后端都启动）

```bash
# 终端 1
docker start dev-mysql

# 终端 2
cd backend && uvicorn main:app --reload --port 8000

# 终端 3
cd frontend && npm run dev
```

打开浏览器访问聊天页面，依次测试：

- 普通闲聊 → 应走 ChatAgent
- "帮我查000001的净值" → 应走 DataQueryAgent → 返回数据
- "筛选规模大于50亿的股票基金" → 应走 FundScreenerAgent
- "生成000001的研究报告" → 应走 ReportAgent

---

## 十、Function Calling Tool 定义示例

```python
# tools/definitions.py

ROUTE_TO_TOOL = {
    "type": "function",
    "function": {
        "name": "route_to",
        "description": "将用户请求路由到合适的 Agent",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_key": {
                    "type": "string",
                    "enum": ["chat", "fund_screen", "data_query", "report"],
                    "description": "目标 Agent 标识"
                },
                "reason": {
                    "type": "string",
                    "description": "路由原因（简短说明）"
                }
            },
            "required": ["agent_key"]
        }
    }
}

EXECUTE_SQL_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": "在基金数据库中执行 SQL 查询（仅支持 SELECT）",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "要执行的 SELECT SQL 语句"
                },
                "explanation": {
                    "type": "string",
                    "description": "这条 SQL 查询的目的说明"
                }
            },
            "required": ["sql"]
        }
    }
}

FILTER_FUNDS_TOOL = {
    "type": "function",
    "function": {
        "name": "filter_funds",
        "description": "按条件筛选基金",
        "parameters": {
            "type": "object",
            "properties": {
                "fund_type": {"type": "string", "description": "基金类型：股票型/债券型/混合型/货币型"},
                "min_size": {"type": "number", "description": "最小规模（亿元）"},
                "max_size": {"type": "number", "description": "最大规模（亿元）"},
                "min_return_ytd": {"type": "number", "description": "最低年初至今收益率(%)"}
            }
        }
    }
}
```

---

## 十一、关键决策记录

| 决策           | 选择                          | 理由                                      |
|--------------|-----------------------------|-----------------------------------------|
| AI 框架        | 自研轻量编排                      | 场景不复杂，外部框架引入适配成本高，后续可迁移                 |
| Agent 是否独立项目 | 否，是 backend 子包              | 同进程调用，避免跨服务通信开销                         |
| Prompt 格式    | Markdown 文件                 | 可读性强、Git diff 友好、支持富格式                  |
| 报告模板格式       | JSON（结构）+ Markdown（prompt）  | JSON 定义节结构和 SQL，Markdown 定义每节的写作 prompt |
| DB 连接层位置     | `backend/db/`（顶层公共）         | AI 和页面共用，避免重复                           |
| SQL 安全       | 第一阶段仅硬性防护                   | 确定性保障，代码简单，快速上线                         |
| 报告生成并行       | `asyncio.gather` 按 group 并行 | 减少总耗时，依赖节等前置完成                          |
| 测试策略         | CLI 独立测试优先                  | 快速迭代，不依赖前端和 HTTP 层                      |

---

## 十二、依赖清单

在 `requirements.txt` 中新增：

```
pymysql          # DB 连接
sqlparse         # SQL 解析与安全校验
```

其余依赖（`fastapi`, `uvicorn`, `openai`）已存在。

---

## 十三、风险与注意事项

1. **DeepSeek-V3 的 Function Calling 能力**：需实测其 tool_calls 返回是否稳定。如果不稳定，Router Agent 可退化为"从 LLM
   文本回复中解析 JSON"的方式，或换用 Function Calling 更稳定的模型（如 Claude）做路由。
2. **流式输出与 Function Calling 的兼容**：Function Calling 循环阶段不产生 SSE 输出，用户会感受到短暂等待。可在
   orchestrator 层先推一条 "正在查询数据..." 的 SSE 提示。
3. **Prompt 版本管理**：Prompt 文件在 Git 中管理，修改需 review。后续可加版本号或 A/B 测试机制。
4. **db_schema.md 与实际表结构同步**：表结构变更时必须同步更新此文件，否则 AI 生成的 SQL 会出错。可考虑写脚本从 DB 自动生成。
