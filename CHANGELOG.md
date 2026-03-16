# CHANGELOG

> 按时间倒序，每次完成开发任务后在顶部追加新条目。

---

## [2026-03-16] 多 Agent 系统实现（Phase A–E 全部完成）

### 完成内容

#### Phase A：骨架搭建
- **`db/connection.py`**：pymysql 连接封装，支持 readonly 账号切换 + 执行超时
- **`db/safety.py`**：SQL 安全校验（去注释→危险关键词→分号检测→SELECT only→白名单表→子查询深度→LIMIT注入），14个单测全部通过
- **`llm/client.py`**：AsyncOpenAI 封装，提供 `chat_completion()` 和 `stream_text()` 异步接口
- **`agents/base.py`**：BaseAgent 基类，实现 Function Calling 循环（非流式检测 tool_calls → 执行工具 → 流式输出最终回复）
- **`agents/chat_agent.py`**：闲聊 Agent，无工具，直接流式输出，含 CLI 测试入口
- **`agents/router_agent.py`**：意图路由，使用 `route_to` tool + 关键词兜底，支持 chat/data_query/fund_screen/report 四种意图
- **`agents/orchestrator.py`**：总调度入口，Route → Agent 分发
- **`tools/registry.py`**：工具注册表，延迟加载避免循环导入
- **`tools/definitions.py`**：ROUTE_TO / EXECUTE_SQL / FILTER_FUNDS / GENERATE_REPORT 四个工具 JSON Schema
- **`prompts/chat.md`**、**`prompts/router.md`**：对应 Agent 的 system prompt
- **`api/chat.py`**（改造）：改为 async，调用 `orchestrator.run()`，SSE 流保持不变

#### Phase B：数据查询能力
- **`templates/db_schema.md`**：6张表的字段说明（含注意事项），注入 DataQueryAgent prompt
- **`tools/sql_executor.py`**：LLM SQL → 安全校验 → 只读执行 → JSON 格式结果
- **`agents/data_query_agent.py`**：覆盖 `_load_prompt` 动态注入 db_schema，含 CLI 测试入口
- **`prompts/data_query.md`**：DataQueryAgent system prompt，含 `{db_schema}` 占位符

#### Phase C：基金筛选能力
- **`tools/fund_filter.py`**：代码生成 SQL（不走 LLM），支持类型/规模/收益率筛选
- **`agents/fund_screener_agent.py`**：FundScreenerAgent，含 CLI 测试入口
- **`prompts/fund_screener.md`**：FundScreenerAgent prompt

#### Phase D：报告生成能力
- **`templates/fund_report.json`**：报告节定义（basic/nav/portfolio/summary），按 parallel_group 并行执行
- **`prompts/report_basic.md`**、**`report_nav.md`**、**`report_portfolio.md`**、**`report_summary.md`**：各节 prompt
- **`prompts/report_writer.md`**：ReportAgent system prompt
- **`tools/report_gen.py`**：按 parallel_group 并行生成各节，asyncio.gather 并发
- **`agents/report_agent.py`**：先 yield 提示语再执行 super().run()

#### Phase E：页面数据接入
- **`services/model_data_service.py`**：`get_yield_curve_data()` / `get_nav_history()`
- **`api/models.py`**（改造）：`GET /api/models/{id}/data` 接入真实 DB，DB 不可用时降级返回空数据
- **`frontend/src/views/models/YieldCurve.vue`**（改造）：`onMounted` 调用 API，有数据时替换 KPI/表格/图表，失败时降级 mock

### 安装依赖
```bash
pip install pymysql sqlparse pytest
```

### MySQL 只读账号（一次性执行）
```bash
docker exec -i dev-mysql mysql -uroot -pdev -e \
  "CREATE USER IF NOT EXISTS 'readonly'@'%' IDENTIFIED BY 'readonly'; \
   GRANT SELECT ON fund_platform.* TO 'readonly'@'%'; FLUSH PRIVILEGES;"
```

### 下一步
- 运行 `pytest tests/test_sql_safety.py` 验证 SQL 安全校验
- 启动后端 `uvicorn main:app --reload --port 8000` 测试完整链路
- 对话测试：普通问答/数据查询/基金筛选/报告生成

---

## [2026-03-13] Phase 2 启动 — 完整平台框架搭建

### 完成内容
- **前端完整重构**：引入 Vue Router + Pinia，从单页聊天升级为多页平台
- **侧边栏导航布局**：`App.vue` 重写为左侧深色侧边栏 + 右侧 `<router-view>` 的整体布局
- **首页 `Home.vue`**：平台 Banner、4 个快速统计指标、模型卡片网格（1 个激活 + 3 个即将上线）
- **AI 问答页 `ChatView.vue`**：独立路由 `/chat`，顶部栏含清空对话按钮，接管原 App.vue 的聊天逻辑
- **收益率曲线 Dashboard `YieldCurve.vue`**：路由 `/models/yield-curve`，含日期筛选、4 个 KPI 卡片、SVG 折线图（mock 数据）、数据明细表格
- **聊天组件迁移**：`components/chat/` 下新建金融主题版本（建议问题改为金融相关）
- **Pinia Chat Store**：`stores/chat.js` 管理消息列表、历史记录、流式状态
- **后端框架扩展**：新增 `api/models.py`（`GET /api/models` 返回模型元数据）、`services/db_service.py`（DB 连接占位）
- **数据库配置**：`config.py` 新增 `ENV` + `DB_CONFIG`，支持 dev（Docker MySQL）/ prod（Doris）双环境切换

### 进行中
- 收益率曲线页使用 mock 数据，尚未接入数据库

### 下一步
- **Phase 2 数据接入**：`db_service.py` 实现真实 MySQL 连接，`YieldCurve.vue` 改为调用后端 API
- **更多模型页面**：基金资产配置分析、基金持仓分析
- **Phase 3 预备**：AI Function Calling，回答中嵌入模型跳转卡片

---

## [2026-03-12] Phase 1 — AI 问答机器人 Demo 初始化

### 完成内容
- 项目初始化：Vue 3 + Vite 前端，FastAPI 后端
- 聊天界面：输入框、消息气泡（左右区分）、Markdown 渲染、流式打字机效果
- 后端 SSE 流式接口：`POST /api/chat`，对接 DeepSeek-V3（东方财富 API 代理）
- 多轮对话：`history` 由前端维护，每轮对话追加后传给后端
- 自动滚动、发送中禁用输入、建议问题卡片等 UX 细节

### 技术要点
- `openai` SDK 兼容接口（`BASE_URL` 指向东财代理，`MODEL=DeepSeek-V3`）
- Vite dev server 代理 `/api` → `http://localhost:8000`
- `markdown-it` 渲染 AI 回答，流式输出期间显示原文防止 Markdown 闪烁
