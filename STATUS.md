# 项目状态

**当前阶段**：Phase 2 — 模型展示页面（进行中）

## 最近完成
- [2026-03-24] 模板 002 重构为 python_func，修复去重 bug，36个测试全部通过，端到端测试通过
  - 002 type 改为 python_func，新建 tools/screen_functions/concept_exposure.py
  - 修复去重 bug：PARTITION BY (c_fd_code, c_report_date, c_stk_code) 正确保留所有股票
  - 解决 MySQL LIMIT-in-subquery 限制：Python 侧先取日期再传参
  - test_load_002 断言更新为 python_func；test_catalog 改用正则匹配模板行
- [2026-03-24] 模板 004 改造为跨区间筛选（python_func），删除模板 001，36个测试全部通过
  - 004 type 改为 python_func，动态生成多 JOIN SQL 支持跨区间条件
  - 新建 tools/screen_functions/performance_filter.py（cross_period_filter 函数）
  - fund_filter.py 新增 cross_period_conditions 参数类型、PERIOD_MAP 模块常量
  - fund_category 改为 fund_category_code 枚举精确匹配（001/002/003/004）
  - 更新 screen_catalog.md、fund_screener.md prompt、测试、文档
- [2026-03-24] 修复 _render_sql 多趟替换导致参数顺序错乱的 bug，改为单趟正则替换，46个测试全部通过
- [2026-03-24] 基金筛选功能大幅扩展：模板系统重构 + 6个新模板（002-007），46个测试全部通过
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
- 模板 004 的 cross_period_filter 使用 INNER JOIN，如果某只基金在目标区间无数据则不返回
