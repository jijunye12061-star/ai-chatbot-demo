# CHANGELOG

> 按时间倒序，每次完成开发任务后在顶部追加新条目。

---

## [2026-03-23] 文档结构重组

### 完成内容
- **`docs/README.md`**（新增）：文档导航首页，所有文档一览
- **`docs/requirements/`**（新增目录）：原大需求文档拆分为 4 个独立文件
  - `01-overview.md`：项目背景、技术栈、三期路线图
  - `02-model-display.md`：模型展示系统需求
  - `03-ai-agent.md`：AI 问答 + 多 Agent 架构设计
  - `04-api-contract.md`：前后端 API 契约
- **`docs/dev/local-db.md`**（新增）：从 `docs/local_dev_db.md` 迁移，同步更新新增表清单（`safety.py` 白名单已自动化）
- **归档**：`local_dev_db.md`、`backend_review.md`、`基金研究团队模型展示平台需求文档.md` 移入 `docs/archive/`
- **`CLAUDE.md`**：更新文档路径引用，修正 Key Architecture Notes 中的过期描述
- **`ARCHITECTURE.md`**：同步更新 docs 目录说明

---

## [2026-03-23] 后端代码质量优化（backend_review.md 全项修复）

### 完成内容

#### P0 安全修复
- **`backend/config.py`**：API Key 改为读取 `LLM_API_KEY` 环境变量，启动时未设置直接报错
- **`.env.example`**（新增）：环境变量模板，`.env` 已在 `.gitignore` 中

#### P0 逻辑修复
- **`backend/agents/base.py`**：FC 循环达到上限（10次）时不再静默结束，yield 兜底提示语

#### P1 性能优化
- **`backend/agents/base.py`**：无工具 Agent（ChatAgent）添加快速路径，直接流式输出，省去一次非流式 LLM 调用
- **`backend/llm/client.py`**：AsyncOpenAI 添加 `httpx.Timeout`（connect=10s, read=120s）和 `max_retries=2`，防止请求挂死

#### P1 健壮性
- **`backend/agents/orchestrator.py`**：路由 `_router.classify()` 失败时降级到 `chat`，防止请求炸掉

#### P1 代码清理
- **`backend/agents/base.py`**：`_execute_tool` 中废弃的 `asyncio.get_event_loop()` 替换为 `asyncio.to_thread()`
- **`backend/utils/serializers.py`**（新增）：提取公共 JSON 序列化函数 `json_default`，处理 Decimal/datetime
- **`backend/tools/fund_filter.py`**、**`backend/tools/sql_executor.py`**：改为 `from utils.serializers import json_default`，移除重复定义

#### P2 代码质量
- **`backend/llm/client.py`**：移除未使用的 `import json`
- **`backend/agents/router_agent.py`**：`today` 从启动时固定改为每次 `classify()` 调用时注入，长时间运行不会过期
- **`backend/api/chat.py`**：`Message.role` 从 `str` 改为 `Role` 枚举（`user`/`assistant`），防止前端传入非法 role
- **`backend/db/safety.py`**：`ALLOWED_TABLES` 从 `table_specs/` 目录自动读取文件名，新增表无需手动同步白名单

### 验证
- `pytest tests/test_sql_safety.py` — **14 passed**（含白名单自动生成后的校验）
- `pytest tests/test_screen_template.py` — **7 passed / 5 skipped**（5个需要 Docker MySQL，已知 DB 未启动）

### 下一步
- Phase 2：更多模型 Dashboard 页面

---

## [2026-03-18] 项目文件审计与清理

### 完成内容

#### 删除废弃文件（8个）
- `backend/services/llm_service.py` — 无引用，已被 `llm/client.py` 取代
- `backend/services/db_service.py` — 无引用，已被 `model_data_service.py` 取代
- `backend/templates/db_schema.md` — 已被两层召回架构取代，DataQueryAgent 不再使用
- `FUND_SCREENER_TEMPLATE_PLAN.md` — 规划已落地
- `TASK_schema_as_skill.md` — 规划已落地
- `data/tb_fd_portfolio_stk.csv` — 已导入 DB，CSV 不再需要
- `import_to_docker.ps1` — 一次性初始化脚本，已完成使命
- `scripts/export_data.py` + `scripts/` 目录

#### 文档整理
- `docs/MULTI_AGENT_PLAN.md` → 移入 `docs/archive/`（新建归档目录）
- `docs/NEW_TABLE_CHECKLIST.md` → 内容并入 `docs/local_dev_db.md`（新增"新增表操作清单"章节），原文件删除
- `docs/local_dev_db.md`：补充新增表操作清单，内容更完整

#### ARCHITECTURE.md 同步更新
- 移除已删文件条目（services/llm_service.py、db_service.py、db_schema.md）
- 新增 `docs/` 目录说明章节
- 修复数据流图（model_data_service 替代旧 db_service 引用）
- 修复重复条目、建表脚本表数（6→9）

---

## [2026-03-18] FundScreenerAgent "SQL 模板填参"架构改造

### 完成内容

#### 模板基础设施（Step 1）
- **`templates/screen_templates/001_return_rank.yaml`**（新增）：第一个筛选模板，按指定区间收益率排名，支持 period_code 枚举、fund_category 可选过滤、trade_date 自动取最新
- **`templates/screen_catalog.md`**（新增）：模板目录摘要，始终注入 FundScreenerAgent prompt
- **`tools/screen_functions/__init__.py`**（新增）：python_func 类型模板的函数存放目录骨架

#### 工具层改造（Step 2）
- **`tools/fund_filter.py`**（重写）：从硬编码 SQL 拼接 → 模板加载 + 参数校验 + SQL 渲染 + 执行；`run_screen_template(template_id, params)` 替代原 `filter_funds()`；内置 safety.validate_sql 防御层
- **`tools/definitions.py`**（修改）：删除 `FILTER_FUNDS_TOOL`，新增 `RUN_SCREEN_TEMPLATE_TOOL`
- **`tools/registry.py`**（修改）：替换工具注册（filter_funds → run_screen_template）

#### Agent 层改造（Step 3）
- **`prompts/fund_screener.md`**（重写）：模板选择工作流，含 `{screen_catalog}` 和 `{today}` 占位符
- **`agents/fund_screener_agent.py`**（改造）：参考 DataQueryAgent 模式，覆盖 `_load_prompt` 注入 screen_catalog + today
- **`prompts/router.md`**（修改）：更新 fund_screen 路由描述，补充"排名""前N""TOP"特征词和3条路由示例

#### 测试（Step 4）
- **`tests/test_screen_template.py`**（新增）：12个 case，覆盖模板加载/参数校验/枚举映射/必填检查/日期格式/limit上限/默认值/catalog文件/prompt占位符

### 验证结果
- `pytest tests/test_screen_template.py -v` — **12 passed**
- `pytest tests/test_sql_safety.py -v` — **14 passed**（已有测试无破坏）

### 架构要点
- 模板 SQL 使用 pymysql 参数化（`%s`），防止 SQL 注入
- 可选条件（category_filter）通过字符串替换插入 SQL 片段，非 LLM 生成
- 模板 type 支持 `sql` 和 `python_func`，后者通过动态 import 调用 `tools/screen_functions/` 下的函数
- 新增模板只需：① 在 `screen_templates/` 下新建 yaml ② 在 `screen_catalog.md` 追加一行

### 下一步
- CLI 集成测试（需 Docker MySQL + LLM）：`python -m agents.fund_screener_agent "筛选近3月收益率前20的基金"`
- 扩充更多筛选模板（如板块持仓占比筛选）

---

## [2026-03-18] DataQueryAgent "Schema as Skill" 改造

### 完成内容

#### 两层召回架构
- **`templates/table_catalog.md`**（新增）：9 张表的极简目录，始终注入 DataQueryAgent prompt，帮助 LLM 快速判断需要哪些表
- **`templates/table_specs/`**（新增，9 个文件）：每张表一个 md，包含实际导出列的字段清单、枚举值、注意事项、查询示例
- **`tools/schema_reader.py`**（新增）：`get_table_schema(tables)` 函数，读取 table_specs/ 下的 md 文件并拼接返回
- **`tools/definitions.py`**（修改）：新增 `GET_TABLE_SCHEMA_TOOL` JSON Schema
- **`tools/registry.py`**（修改）：注册 `get_table_schema` 工具
- **`prompts/data_query.md`**（重写）：两层召回逻辑，`{table_catalog}` + `{today}` 占位符，明确 nav_daily（小数格式）vs perform_abs（已是%）的数据格式差异
- **`agents/data_query_agent.py`**（改造）：注入 table_catalog 替代全量 db_schema，tool_names 增加 `get_table_schema`

#### 白名单扩展
- **`db/safety.py`**（修改）：ALLOWED_TABLES 新增 `tb_fd_perform_abs`、`tb_dict_params`、`tb_fd_tag_asset_eq`
- **`tests/test_sql_safety.py`**（修改）：同步更新白名单测试列表，14 个 case 全部通过

#### 文档更新
- **`docs/local_dev_db.md`**：表列表从 6 张更新为 9 张，补充预估行数
- `ARCHITECTURE.md` + `CHANGELOG.md` 同步更新

### 验证结果
- `pytest tests/test_sql_safety.py` — 14 passed
- CLI 测试 1-9：LLM 正确先调用 `get_table_schema` 再写 SQL，选表准确，字段正确

### 下一步
- Phase 2 更多模型展示页面
- Phase 3 AI Function Calling 推荐模型

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
