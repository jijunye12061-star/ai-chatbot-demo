# ARCHITECTURE

> 代码地图。**新增、删除、重命名文件时同步更新本文件。**

---

## 整体结构

```
project/
├── frontend/          # Vue 3 + Vite SPA
├── backend/           # FastAPI 后端
├── docs/              # 需求文档
├── data/              # 本地测试数据（SQL schema、CSV）
├── CLAUDE.md          # 项目总览 + 开发规范（本文件的上级）
├── ARCHITECTURE.md    # 本文件：代码地图
└── CHANGELOG.md       # 开发日志
```

---

## Frontend (`frontend/src/`)

### 入口

| 文件        | 职责                                            |
|-----------|-----------------------------------------------|
| `main.js` | 创建 Vue 应用，注册 Pinia、Vue Router，挂载到 `#app`      |
| `App.vue` | 根组件：左侧侧边栏导航 + 右侧 `<router-view>`，控制侧边栏展开/折叠状态 |

### 路由 (`router/`)

| 文件                | 职责                                                                               |
|-------------------|----------------------------------------------------------------------------------|
| `router/index.js` | Vue Router 配置，三条路由：`/`（Home）、`/chat`（ChatView）、`/models/yield-curve`（YieldCurve） |

### 状态管理 (`stores/`)

| 文件               | 职责                                                                      |
|------------------|-------------------------------------------------------------------------|
| `stores/chat.js` | Pinia store：管理 `messages`、`history`、`streaming` 状态，封装 `send()` 方法调用 LLM |

### 页面视图 (`views/`)

| 文件                            | 路由                    | 职责                                                    |
|-------------------------------|-----------------------|-------------------------------------------------------|
| `views/Home.vue`              | `/`                   | 平台首页：Banner、统计指标行、模型卡片网格（4 张，1 激活 3 占位）               |
| `views/ChatView.vue`          | `/chat`               | AI 问答页：顶部栏 + ChatWindow + ChatInput，从 Chat Store 读取状态 |
| `views/models/YieldCurve.vue` | `/models/yield-curve` | 收益率曲线 Dashboard：日期筛选、KPI 卡片、SVG 折线图（当前 mock 数据）、数据表格  |

> 新增模型页面时，在 `views/models/` 下创建 `.vue` 文件，并在 `router/index.js` 中注册路由。

### 组件 (`components/`)

#### `components/chat/`（当前使用）

| 文件                       | 职责                                                  |
|--------------------------|-----------------------------------------------------|
| `chat/ChatWindow.vue`    | 消息列表容器：空状态（建议问题卡片）+ 消息气泡列表 + 自动滚动                   |
| `chat/MessageBubble.vue` | 单条消息气泡：区分 user/assistant 样式，assistant 消息渲染 Markdown |
| `chat/ChatInput.vue`     | 输入框组件：自动高度 textarea、发送按钮、Enter 发送 / Shift+Enter 换行  |

#### `components/charts/`（待创建）

> Phase 2 数据接入时，在此处添加 ECharts 等图表组件。

#### `components/common/`（待创建）

> 未来放通用 UI 组件（DatePicker、ExcelExport 等）。

### API 封装 (`api/`)

| 文件              | 职责                                                                  |
|-----------------|---------------------------------------------------------------------|
| `api/chat.js`   | `sendMessage()`：POST `/api/chat`，读取 SSE 流，回调通知 chunk / done / error |
| `api/models.js` | `fetchModels()`：GET `/api/models`，返回模型元数据列表                         |

---

## Backend (`backend/`)

### 入口

| 文件          | 职责                                                                            |
|-------------|-------------------------------------------------------------------------------|
| `main.py`   | FastAPI 应用入口：注册 CORS、挂载 `chat_router` 和 `models_router`                       |
| `config.py` | 全局配置：LLM（API_KEY / BASE_URL / MODEL）、环境变量 `ENV`（dev/prod）、`DB_CONFIG` 数据库连接参数 |

### 路由 (`api/`)

| 文件              | 路由                | 职责                                                                                 |
|-----------------|-------------------|------------------------------------------------------------------------------------|
| `api/chat.py`   | `POST /api/chat`  | 接收 `{message, history}`，调用 `llm_service.stream_chat()`，返回 `StreamingResponse`（SSE） |
| `api/models.py` | `GET /api/models` | 返回平台所有模型的元数据（id、名称、状态等）；`GET /api/models/{id}/data` 占位（待接入 DB）                     |

### 服务层 (`services/`)

| 文件                               | 职责                                                                             |
|----------------------------------|--------------------------------------------------------------------------------|
| `services/model_data_service.py` | 模型展示页面数据查询：`get_yield_curve_data()` / `get_nav_history()`，被 `api/models.py` 引用 |

### 数据库层 (`db/`) — 公共层，AI + 页面共用

| 文件                 | 职责                                                             |
|--------------------|----------------------------------------------------------------|
| `db/connection.py` | `get_connection(readonly)` / `execute_query()`，支持只读账号切换        |
| `db/safety.py`     | SQL 安全校验：危险关键词检测 → 单语句 → SELECT only → 白名单表 → 子查询深度 → LIMIT 注入 |

### LLM 层 (`llm/`)

| 文件              | 职责                                                                          |
|-----------------|-----------------------------------------------------------------------------|
| `llm/client.py` | AsyncOpenAI 封装：`chat_completion()`（非流式）、`stream_text()`（流式 async generator） |

### 多 Agent 层 (`agents/`)

| 文件                              | 职责                                                                     |
|---------------------------------|------------------------------------------------------------------------|
| `agents/orchestrator.py`        | 总调度入口：message + history → RouterAgent → 分发到具体 Agent                    |
| `agents/base.py`                | BaseAgent 基类：Function Calling 循环（检测 tool_calls → 执行 → 流式最终回复）          |
| `agents/router_agent.py`        | 意图路由：LLM tool_call + 关键词兜底，返回 agent_key                                |
| `agents/chat_agent.py`          | 兜底闲聊 Agent，无工具                                                         |
| `agents/data_query_agent.py`    | 数据查询 Agent，注入 table_catalog，使用 get_table_schema + execute_sql 工具（两层召回） |
| `agents/fund_screener_agent.py` | 基金筛选 Agent，注入 screen_catalog，使用 run_screen_template 工具（模板填参架构）         |
| `agents/report_agent.py`        | 报告生成 Agent，先提示再调用 generate_fund_report 工具                              |

### 工具层 (`tools/`)

| 文件                          | 职责                                                                                                       |
|-----------------------------|----------------------------------------------------------------------------------------------------------|
| `tools/registry.py`         | 工具注册表，延迟加载避免循环导入                                                                                         |
| `tools/definitions.py`      | 所有工具的 JSON Schema：route_to / execute_sql / run_screen_template / generate_fund_report / get_table_schema / get_dimension_list / ask_data_agent |
| `tools/sql_executor.py`     | LLM SQL → safety.validate_sql → 只读执行 → JSON 结果                                                           |
| `tools/schema_reader.py`    | `get_table_schema(tables)` → 读取 templates/table_specs/*.md → 返回拼接的字段说明                                   |
| `tools/fund_filter.py`      | 模板加载 + 参数校验 + `_render_sql`（具名占位符 {:x}/{*x}/{?x}/{@x}/{#sw_industry}）+ 执行（`run_screen_template`）        |
| `tools/dimension_lookup.py` | `get_dimension_list(dim_type)` → 查 tb_dict_params → 返回概念/行业码 JSON                                        |
| `tools/data_agent_bridge.py`| `async ask_data_agent(question)` → 实例化 DataQueryAgent，async for 收集流式输出后返回                              |
| `tools/screen_functions/`   | Python 函数筛选模块（type=python_func 模板用）                                                                       |
| `tools/screen_functions/performance_filter.py` | 模板004 执行函数：`cross_period_filter`，动态生成跨区间多 JOIN SQL      |
| `tools/report_gen.py`       | 按 fund_report.json 模板，parallel_group 并行生成各节报告                                                            |

### Prompt 文件 (`prompts/`)

| 文件                            | 用途                                                                   |
|-------------------------------|----------------------------------------------------------------------|
| `prompts/chat.md`             | ChatAgent system prompt                                              |
| `prompts/router.md`           | RouterAgent system prompt，定义4种意图和路由规则                                |
| `prompts/data_query.md`       | DataQueryAgent prompt，含 `{table_catalog}` 和 `{today}` 占位符，两层召回工作流程说明 |
| `prompts/fund_screener.md`    | FundScreenerAgent prompt                                             |
| `prompts/report_writer.md`    | ReportAgent system prompt                                            |
| `prompts/report_basic.md`     | 基础信息节 prompt                                                         |
| `prompts/report_nav.md`       | 净值表现节 prompt                                                         |
| `prompts/report_portfolio.md` | 持仓结构节 prompt                                                         |
| `prompts/report_summary.md`   | 综合评价节 prompt                                                         |

### 模板文件 (`templates/`)

| 文件                                                | 用途                                                     |
|---------------------------------------------------|--------------------------------------------------------|
| `templates/table_catalog.md`                      | 9张表的极简目录（一行一表），始终注入 DataQueryAgent prompt              |
| `templates/table_specs/`                          | 每张表一个 md 文件，按需通过 get_table_schema 工具加载（含字段清单、枚举值、查询示例） |
| `templates/fund_report.json`                      | 报告节定义（id/title/sql/parallel_group/depends_on）          |
| `templates/screen_catalog.md`                     | 基金筛选模板目录摘要，始终注入 FundScreenerAgent prompt               |
| `templates/screen_templates/`                     | 筛选模板 YAML 文件（每个模板含 id/params/sql/type）                 |
| `templates/screen_templates/002_concept_exposure.yaml`| 模板002：概念主题曝露度筛选（{*concept_codes}，四层CTE）                   |
| `templates/screen_templates/003_industry_exposure.yaml`| 模板003：申万行业曝露度筛选（{#sw_industry}，支持一/二/三级混合）             |
| `templates/screen_templates/004_performance_filter.yaml`| 模板004：跨区间多条件业绩筛选（python_func，动态生成多 JOIN SQL）           |
| `templates/screen_templates/005_tag_eq.yaml`          | 模板005：权益基金标签筛选（tb_fd_tag_asset_eq）                          |
| `templates/screen_templates/006_tag_fi.yaml`          | 模板006：固收+基金标签筛选（tb_fd_tag_asset_fi，生产环境）                  |
| `templates/screen_templates/007_tag_mix.yaml`         | 模板007：混合基金标签筛选（tb_fd_tag_asset_mix，生产环境）                  |
| `templates/table_specs/tb_stk_industry.md`            | A股行业归属表规格，dev 适配版（2 个截面）                                 |
| `templates/table_specs/tb_stk_concept.md`             | A股概念归属表规格，dev 适配版（2 个截面）                                 |
| `templates/table_specs/tb_fd_tag_asset_fi.md`         | 新增：固收+基金标签表规格（dev 无此表，生产可用）                             |
| `templates/table_specs/tb_fd_tag_asset_mix.md`        | 新增：混合基金标签表规格（dev 无此表，生产可用）                             |

### 工具函数 (`utils/`)

| 文件                        | 职责                                              |
|---------------------------|-------------------------------------------------|
| `utils/serializers.py`    | 公共 JSON 序列化辅助：处理 Decimal / datetime 类型，供工具层共用 |

### 测试 (`tests/`)

| 文件                              | 用途                                                 |
|---------------------------------|----------------------------------------------------|
| `tests/test_sql_safety.py`      | SQL 安全校验单测（14个 case，无需 DB/LLM）                     |
| `tests/test_screen_template.py` | 模板系统单测（12个 case：模板加载/参数校验/枚举映射/prompt注入，无需 DB/LLM） |

---

## 数据 (`data/`)

| 文件                      | 职责                              |
|-------------------------|---------------------------------|
| `data/schema_mysql.sql` | 建表脚本（11 张表），用于初始化本地 Docker MySQL |
| `data/import.py` | CSV 批量导入脚本：读 11 个 CSV → 类型转换 → INSERT（pandas + mysql-connector） |
| `data/test_chat.py` | 后端 AI 问答测试脚本：直接 POST /api/chat，流式打印，无需前端 |

详细说明见 `docs/local_dev_db.md`：容器名 `dev-mysql`、端口 3306、库名 `fund_platform`、root/dev。

## 文档 (`docs/`)

| 文件/目录                                      | 用途                                           |
|--------------------------------------------|----------------------------------------------|
| `docs/README.md`                           | 文档导航首页，所有文档的入口索引                             |
| `docs/requirements/01-overview.md`         | 项目背景、技术栈、三期路线图                               |
| `docs/requirements/02-model-display.md`    | 模型展示系统设计需求                                   |
| `docs/requirements/03-ai-agent.md`         | AI 问答 + 多 Agent 架构设计                         |
| `docs/requirements/04-api-contract.md`     | 前后端 API 契约（请求/响应格式、SSE 协议）                   |
| `docs/dev/local-db.md`                     | 本地开发数据库说明：容器信息、建表、数据导入/导出、新增表操作清单            |
| `docs/specs/2026-03-24-fund-screening-design.md` | 基金筛选功能设计文档（模板002-007 + 重构方案）           |
| `docs/fund_screener_cases.md`              | 新增：基金筛选问题池（9个场景 case，含期望路径和状态）              |
| `docs/table_specs_source/`                 | 各表的规格定义源文件（含 16 张表，含 7 张未实现的股票/债券表），是扩表的前置参考 |
| `docs/archive/`                            | 已归档的历史文档（仅存档，不参与开发）                          |

---

## 关键数据流

### AI 问答流（多 Agent 架构）

```
用户输入
  → ChatInput.vue (emit 'send')
  → ChatView.vue → useChatStore().send()
  → api/chat.js sendMessage() → POST /api/chat
  → backend: api/chat.py (async) → orchestrator.run()
    → RouterAgent.classify() → 识别意图（chat/data_query/fund_screen/report）
    → 分发到对应 Agent.run()
      → BaseAgent FC循环：chat_completion(tools) → 有 tool_calls → 执行工具 → 继续
      → 最终：stream_text() 流式输出
  → yield SSE chunks → onChunk() 追加到 message.content
  → MessageBubble.vue 实时渲染
  → onDone() 触发 Markdown 渲染
```

### 模型数据流

```
YieldCurve.vue 挂载
  → api/models.js fetchModels() → GET /api/models/{id}/data
  → backend: api/models.py → model_data_service.get_yield_curve_data()
  → MySQL / Doris → 返回数据
  → 图表渲染
```

---

## 待办文件（尚未创建）

| 文件                                               | 创建时机                                 |
|--------------------------------------------------|--------------------------------------|
| `backend/tools/recommend_model.py`               | Phase 3：AI Function Calling tool 定义  |
| `frontend/src/components/charts/LineChart.vue`   | Phase 2：YieldCurve 接入真实图表库（ECharts）时 |
| `frontend/src/components/common/ExcelExport.vue` | Phase 2：数据导出功能时                      |
| `views/models/AssetAllocation.vue`               | Phase 2：基金资产配置 Dashboard             |
| `views/models/PortfolioAnalysis.vue`             | Phase 2：基金持仓分析 Dashboard             |
