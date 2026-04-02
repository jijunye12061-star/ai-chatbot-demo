# ARCHITECTURE

> 代码地图。**新增、删除、重命名文件时同步更新本文件。**

---

## 整体结构

```
project/
├── frontend/          # Vue 3 + Vite SPA
├── backend/           # FastAPI 后端
├── docs/              # 需求 + 开发文档
├── data/              # 测试脚本
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
| `chat/MessageBubble.vue` | Claude 风格消息气泡：user 右对齐气泡，assistant 无气泡左对齐，支持 Markdown 渲染 + thinking/result 嵌套组件 |
| `chat/ChatInput.vue`     | 输入框组件：自动高度 textarea、发送按钮、Enter 发送 / Shift+Enter 换行  |
| `chat/ThinkingTimeline.vue` | 思考时间轴组件：折叠/展开状态切换，running/done/error 胶囊状态点，YAML 格式思考内容展示 |
| `chat/ResultTable.vue`   | 结构化查询结果预览表格：前 5 条数据展示 + SheetJS 库 Excel 下载功能 |

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
| `api/chat.py`   | `POST /api/chat`  | 接收 `{message, history}`，调用 `orchestrator.run()`，透传 base.py 预格式化 SSE 事件（thinking/content/result_data）给前端 |
| `api/models.py` | `GET /api/models` | 返回平台所有模型的元数据（id、名称、状态等）；`GET /api/models/{id}/data` 占位（待接入 DB）                     |

### 服务层 (`services/`)

| 文件                               | 职责                                                                             |
|----------------------------------|--------------------------------------------------------------------------------|
| `services/model_data_service.py` | 模型展示页面数据查询：`get_yield_curve_data()` / `get_nav_history()`，被 `api/models.py` 引用 |

### 数据库层 (`db/`) — 公共层，AI + 页面共用

| 文件                 | 职责                                                             |
|--------------------|----------------------------------------------------------------|
| `db/connection.py` | `execute_query()` 统一入口：dev 走远程 SQL 服务（HTTP），prod 走 Doris 直连（pymysql） |
| `db/safety.py`     | SQL 安全校验：危险关键词检测 → 单语句 → SELECT only → 白名单表 → 子查询深度 → LIMIT 注入 |

### LLM 层 (`llm/`)

| 文件              | 职责                                                                          |
|-----------------|-----------------------------------------------------------------------------|
| `llm/client.py` | AsyncOpenAI 封装：`chat_completion()`（非流式）、`stream_text()`（流式 async generator） |

### Agent 层 (`agents/`)

| 文件                          | 职责                                                                                       |
|-----------------------------|------------------------------------------------------------------------------------------|
| `agents/orchestrator.py`    | 总调度入口：message + history → 直接实例化 MainAgent → 流式输出（已简化，无 RouterAgent）                    |
| `agents/base.py`            | BaseAgent 基类：FC 循环 + 预格式化 SSE 事件 yield，按 type 分为 thinking/content/result_data，供前端路由处理                          |
| `agents/main_agent.py`      | 单一主 Agent：注入 table_catalog + screen_catalog，使用全部 5 个工具，处理数据查询/基金筛选/报告/闲聊 |
| `agents/report_agent.py`    | 报告生成 subagent，先提示再调用 generate_fund_report 工具，由 report_agent_bridge 调用               |

### 工具层 (`tools/`)

| 文件                              | 职责                                                                                              |
|---------------------------------|--------------------------------------------------------------------------------------------------|
| `tools/registry.py`             | 工具注册表，延迟加载避免循环导入                                                                                 |
| `tools/definitions.py`          | 所有工具的 JSON Schema：execute_sql / get_table_schema / get_dimension_list / get_screen_guide / generate_fund_report（共 5 个）|
| `tools/tool_result.py`          | ToolResult 数据类：summary（描述信息）+ full_rows（完整数据行）+ columns（列定义），sql_executor 的结构化返回值       |
| `tools/sql_executor.py`         | LLM SQL → safety.validate_sql → 只读执行 → ToolResult（包含 summary/full_rows/columns）                    |
| `tools/schema_reader.py`        | `get_table_schema(tables)` → 读取 templates/table_specs/*.md → 返回拼接的字段说明                           |
| `tools/dimension_lookup.py`     | `get_dimension_list(dim_type)` → 查 tb_dict_params → 返回概念/行业码 JSON                               |
| `tools/screen_guide_reader.py`  | `get_screen_guide(guide_name)` → 读取 templates/screen_guides/*.md → 返回筛选知识文档，供 AI 写 SQL 参考        |
| `tools/report_agent_bridge.py`  | `async ask_report_agent(fund_code)` → 实例化 ReportAgent，收集流式输出后返回                                  |
| `tools/report_gen.py`           | 按 fund_report.json 模板，parallel_group 并行生成各节报告                                                    |

### Prompt 文件 (`prompts/`)

| 文件                            | 用途                                                                                              |
|-------------------------------|--------------------------------------------------------------------------------------------------|
| `prompts/main_agent.md`       | MainAgent 统一 system prompt，含 `{table_catalog}` / `{screen_catalog}` / `{today}` 占位符，覆盖全部意图 |
| `prompts/report_writer.md`    | ReportAgent system prompt                                                                        |
| `prompts/report_basic.md`     | 基础信息节 prompt                                                                                    |
| `prompts/report_nav.md`       | 净值表现节 prompt                                                                                    |
| `prompts/report_portfolio.md` | 持仓结构节 prompt                                                                                    |
| `prompts/report_summary.md`   | 综合评价节 prompt                                                                                    |

### 模板文件 (`templates/`)

| 文件                                        | 用途                                                                              |
|-------------------------------------------|---------------------------------------------------------------------------------|
| `templates/table_catalog.md`              | 9张表的极简目录（一行一表），始终注入 MainAgent prompt                                           |
| `templates/table_specs/`                  | 每张表一个 md 文件，按需通过 get_table_schema 工具加载（含字段清单、枚举值、查询示例）                          |
| `templates/fund_report.json`              | 报告节定义（id/title/sql/parallel_group/depends_on）                                   |
| `templates/screen_catalog.md`             | 基金筛选知识文档索引，始终注入 MainAgent prompt，指引 AI 调用 get_screen_guide 获取详细知识               |
| `templates/screen_guides/`                | 基金筛选知识文档（6 个 .md，按需通过 get_screen_guide 加载，AI 据此写 SQL）                          |
| `templates/screen_guides/concept_exposure.md`   | 概念主题曝露度筛选知识（tb_stk_concept + tb_fd_portfolio_stk，CTE 写法）                 |
| `templates/screen_guides/industry_exposure.md`  | 申万行业曝露度筛选知识（tb_stk_industry，一/二/三级混合 LIKE 匹配）                          |
| `templates/screen_guides/performance_filter.md` | 业绩指标筛选知识（tb_fd_perform_abs，跨区间动态 JOIN 写法）                              |
| `templates/screen_guides/tag_equity.md`         | 权益基金标签筛选知识（tb_fd_tag_asset_eq，枚举值说明）                                   |
| `templates/screen_guides/tag_fixed_income.md`   | 固收+基金标签筛选知识（tb_fd_tag_asset_fi，生产环境）                                   |
| `templates/screen_guides/tag_mixed.md`          | 混合基金标签筛选知识（tb_fd_tag_asset_mix，生产环境）                                   |
| `templates/table_specs/tb_stk_industry.md`      | A股行业归属表规格，dev 适配版（2 个截面）                                               |
| `templates/table_specs/tb_stk_concept.md`       | A股概念归属表规格，dev 适配版（2 个截面）                                               |
| `templates/table_specs/tb_fd_tag_asset_fi.md`   | 固收+基金标签表规格（dev 无此表，生产可用）                                               |
| `templates/table_specs/tb_fd_tag_asset_mix.md`  | 混合基金标签表规格（dev 无此表，生产可用）                                               |

### 工具函数 (`utils/`)

| 文件                        | 职责                                              |
|---------------------------|-------------------------------------------------|
| `utils/serializers.py`    | 公共 JSON 序列化辅助：处理 Decimal / datetime 类型，供工具层共用 |
| `utils/conv_logger.py`    | 对话日志：每次请求写一个独立 log 文件到 `backend/logs/`，contextvars 保证并发隔离 |

### 测试 (`tests/`)

| 文件                                 | 用途                                                             |
|------------------------------------|----------------------------------------------------------------|
| `tests/test_sql_safety.py`         | SQL 安全校验单测（14个 case，无需 DB/LLM）                               |
| `tests/test_screen_guide_reader.py`| screen_guide_reader 单测（guide 加载/不存在错误处理，无需 DB/LLM）            |
| `tests/test_definitions.py`        | tools/definitions.py 工具定义单测（确认 5 个工具 schema 完整，无需 DB/LLM）     |
| `tests/test_orchestrator.py`       | orchestrator 集成测试（MainAgent 路径，无需真实 LLM）                      |

---

## 数据 (`data/`)

| 文件                 | 职责                                         |
|--------------------|--------------------------------------------|
| `data/test_chat.py` | 后端 AI 问答测试脚本：直接调用 orchestrator，流式打印，无需启动后端服务 |

> 开发数据库说明见 `docs/dev/remote-db.md`。

## 文档 (`docs/`)

| 文件/目录                                      | 用途                                           |
|--------------------------------------------|----------------------------------------------|
| `docs/README.md`                           | 文档导航首页，所有文档的入口索引                             |
| `docs/requirements/01-overview.md`         | 项目背景、技术栈、三期路线图                               |
| `docs/requirements/02-model-display.md`    | 模型展示系统设计需求                                   |
| `docs/requirements/03-ai-agent.md`         | AI 问答 + 多 Agent 架构设计                         |
| `docs/requirements/04-api-contract.md`     | 前后端 API 契约（请求/响应格式、SSE 协议）                   |
| `docs/dev/remote-db.md`                    | 开发数据库说明：远程 SQL 服务架构、内网部署、Token 认证、新增表操作清单   |
| `docs/specs/2026-03-24-fund-screening-design.md` | 基金筛选功能设计文档（模板002-007 + 重构方案）           |
| `docs/fund_screener_cases.md`              | 新增：基金筛选问题池（9个场景 case，含期望路径和状态）              |
| `docs/table_specs_source/`                 | 各表的规格定义源文件（含 16 张表，含 7 张未实现的股票/债券表），是扩表的前置参考 |
| `docs/archive/`                            | 已归档的历史文档（仅存档，不参与开发）                          |

---

## 关键数据流

### AI 问答流（Single MainAgent 架构）

```
用户输入
  → ChatInput.vue (emit 'send')
  → ChatView.vue → useChatStore().send()
  → api/chat.js sendMessage() → POST /api/chat
  → backend: api/chat.py (async) → orchestrator.run()
    → MainAgent.run()（直接，无路由步骤）
      → BaseAgent FC循环：chat_completion(tools) → 有 tool_calls → 执行工具 → 继续
        可调用工具：execute_sql / get_table_schema / get_dimension_list
                    get_screen_guide / generate_fund_report（→ ReportAgent subagent）
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
  → execute_query() → 远程 SQL 服务(dev) / Doris 直连(prod)
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
