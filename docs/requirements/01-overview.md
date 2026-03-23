# 项目概述

## 背景

基金研究团队希望将自身研究成果对外展示，构建一个面向客户的 Web 平台。平台包含两大核心能力：

- **模型展示系统**：以 Dashboard / 报告形式展示各类金融模型的结果，支持交互筛选和数据下载
- **AI 问答机器人**：智能对话入口，可根据用户提问自动推荐相关模型页面，引导用户深入探索

两者通过 AI 的 Function Calling 能力联动——AI 在回答中结构化返回推荐的模型页面，前端渲染为可点击的链接卡片。

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite | SPA，Composition API，`<script setup>` |
| 后端 | FastAPI (Python 3.11+) | 异步框架，SSE 流式返回 |
| 数据库 | Doris（生产）/ MySQL 8.0（本地开发） | Doris 兼容 MySQL 语法，开发环境用 Docker 模拟 |
| 大模型 | DeepSeek-V3（东财 API 代理，OpenAI SDK 兼容） | 通过 `backend/config.py` 可切换 |
| 通信 | SSE（Server-Sent Events） | AI 回答流式输出（打字机效果） |

**环境切换**：`APP_ENV` 环境变量区分 `dev`（Docker MySQL）/ `prod`（Doris），`config.py` 处理两套 DB 配置。

---

## 三期开发路线图

### Phase 1 — AI 问答机器人 Demo ✅ 已完成

- Vue 3 + FastAPI 项目脚手架
- 聊天界面（流式输出、Markdown 渲染、多轮对话）
- 多 Agent 系统（Router → Orchestrator → Agent → Tool）
- 四大问答场景：闲聊、数据查询、基金筛选、报告生成

### Phase 2 — 模型展示页面（进行中）

- 侧边栏导航 + 路由框架 ✅
- 收益率曲线 Dashboard + DB 数据接入 ✅
- 更多模型 Dashboard（资产配置分析、持仓分析）
- 通用图表组件（ECharts）、数据导出（Excel）

### Phase 3 — AI 联动（待启动）

- Function Calling：AI 回答中嵌入模型跳转卡片
- 用户权限控制（可选）
- 对话持久化存储（可选）

---

## 暂不实现

- 用户登录 / 鉴权
- 对话持久化存储
- 多轮对话的 token 截断策略
- 移动端适配
- 前端主题深度定制
