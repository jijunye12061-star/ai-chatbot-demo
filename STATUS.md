# 项目状态

**当前阶段**：Single-Agent 重构已完成，等待合并到 main

## 最近完成
- [2026-03-25] Multi-Agent → Single MainAgent 重构（feature/single-agent-refactor 分支）
  - 删除 RouterAgent / ChatAgent / DataQueryAgent / FundScreenerAgent
  - 删除 YAML 模板（screen_templates/）及 fund_filter.py / data_agent_bridge.py
  - 新增 agents/main_agent.py（单 Agent，Function Calling 循环）
  - 新增 prompts/main_agent.md（统一 system prompt，含 table_catalog + screen_catalog）
  - 基金筛选改为 AI 直接写 SQL + get_screen_guide 加载知识文档（6 个 .md）
  - ReportAgent 保留为 subagent，通过 report_agent_bridge.py 调用
  - LLM 调用：原 2+ 次 → 现 1 次起步
  - 请求路径：User → Orchestrator → MainAgent → 工具（→ ReportAgent subagent）
  - 测试：21 passed（含 screen_guide_reader / definitions / orchestrator 集成测试）

## 进行中
（无）

## 下一步
1. 合并 feature/single-agent-refactor 到 main
2. 前后端联调验证（uvicorn + npm run dev）
3. Phase 2：持仓分析 Dashboard（tb_fd_portfolio_stk）

## 关键约束 / 注意事项
- LLM API Key 通过 `backend/.env` 注入（不提交 git）
- SQL 白名单从 `backend/templates/table_specs/` 自动读取文件名
- tb_fd_tag_asset_fi / tb_fd_tag_asset_mix 在 dev 环境无表，生产才可用
- get_screen_guide 加载 templates/screen_guides/*.md，AI 据此自写 SQL
- 聊天组件统一在 `src/components/chat/`，Chat Store 在 `src/stores/chat.js`
- 后端启动：`cd backend && uvicorn main:app --reload --port 8000`（自动加载 .env）
- dev 数据范围：nav_daily/perform_abs 仅 2025-12；持仓/资产配置/分类 3 个季度截面
