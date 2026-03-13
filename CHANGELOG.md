# CHANGELOG

> 按时间倒序，每次完成开发任务后在顶部追加新条目。

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
