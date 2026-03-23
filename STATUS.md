# 项目状态

**当前阶段**：Phase 2 — 模型展示页面（进行中）

## 最近完成
- [2026-03-23] 文档结构重组（docs/ 拆分为 requirements/ + dev/，新增 README.md 导航）
- [2026-03-23] 后端代码质量优化（backend_review.md 全项修复：API Key 环境变量、FC 兜底、LLM 超时、序列化器提取等）
- [2026-03-18] DataQueryAgent + FundScreenerAgent 模板化改造，多 Agent 框架全面落地

## 进行中
（无）

## 下一步
- Phase 2：更多模型 Dashboard 页面（资产配置分析、持仓分析）
- 通用图表组件（ECharts）、数据导出（Excel）

## 关键约束 / 注意事项
- LLM API Key 通过环境变量 `LLM_API_KEY` 注入（`.env` 文件，不提交 git）
- SQL 白名单从 `backend/templates/table_specs/` 自动读取文件名，新增表只需加 `.md`
- 聊天组件统一在 `src/components/chat/`，Chat Store 在 `src/stores/chat.js`
- 后端启动需 `cd backend && LLM_API_KEY=xxx uvicorn main:app --reload --port 8000`
