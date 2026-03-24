# 项目状态

**当前阶段**：Phase 2 — 模型展示页面（进行中）

## 最近完成
- [2026-03-24] 基金筛选功能大幅扩展：模板系统重构 + 6个新模板（002-007），44个测试全部通过
  - fund_filter.py 重构为具名占位符架构（{:x} {*x} {?x} {@x} {#sw_industry}）
  - 新增 dimension_lookup.py（概念/行业维度查询）、data_agent_bridge.py（DataAgent委托）
  - 新增模板：概念曝露度/申万行业曝露度/多条件业绩/权益+固收+混合标签筛选
  - db/safety.py 子查询深度限制 2→4
- [2026-03-24] AI 问答后端测试通过：DataQueryAgent/FundScreenerAgent/ChatAgent 全链路跑通
- [2026-03-23] DB 重建完成：11 张表全部建好并导入 CSV 数据（共 ~27 万行）

## 进行中
（无）

## 下一步
1. Phase 2：持仓分析 Dashboard（tb_fd_portfolio_stk：前十大持仓、行业分布）
2. Phase 2：资产配置分析 Dashboard（tb_fd_asset_allocation：股债现金比例趋势）
3. YieldCurve.vue 接入真实 DB 数据（当前 mock）

## 关键约束 / 注意事项
- LLM API Key 通过 `backend/.env` 注入（不提交 git）
- SQL 白名单从 `backend/templates/table_specs/` 自动读取文件名（含新增 tb_fd_tag_asset_fi/mix）
- tb_fd_tag_asset_fi / tb_fd_tag_asset_mix 在 dev 环境无表，模板006/007 生产才可用
- 聊天组件统一在 `src/components/chat/`，Chat Store 在 `src/stores/chat.js`
- 后端启动：`cd backend && uvicorn main:app --reload --port 8000`（自动加载 .env）
- dev 数据范围：nav_daily/perform_abs 仅 2025-12；持仓/资产配置/分类 3 个季度截面；行业/概念 2 个截面
