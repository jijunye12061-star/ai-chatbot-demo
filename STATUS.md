# 项目状态

**当前阶段**：Phase 2 — 模型展示页面（进行中）

## 最近完成
- [2026-03-23] DB 重建 + 模板更新：重写 schema_mysql.sql（11 张表）、新增 data/import.py、补全所有 table_specs 文档（新增 tb_stk_industry/concept）、新建 data/test_chat.py
- [2026-03-23] 文档结构重组 + 后端代码质量优化
- [2026-03-18] DataQueryAgent + FundScreenerAgent 模板化改造，多 Agent 框架全面落地

## 进行中
- Task 3：Docker DB 重建 + 数据导入（需手动执行，见下方说明）

## 下一步
1. 手动执行 DB 重建（见下方）
2. 启动后端后用 `python data/test_chat.py` 测试 AI 问答
3. Phase 2：更多模型 Dashboard 页面（资产配置分析、持仓分析）

## 手动执行 DB 重建

```bash
docker start dev-mysql
docker exec -i dev-mysql mysql -uroot -pdev fund_platform < data/schema_mysql.sql
cd data && python import.py
```

预期：11 张表，总行数约 27.3 万行

## 关键约束 / 注意事项
- LLM API Key 通过环境变量 `LLM_API_KEY` 注入（`.env` 文件，不提交 git）
- SQL 白名单从 `backend/templates/table_specs/` 自动读取文件名，新增表（tb_stk_industry/concept）已加入
- 聊天组件统一在 `src/components/chat/`，Chat Store 在 `src/stores/chat.js`
- 后端启动需 `cd backend && LLM_API_KEY=xxx uvicorn main:app --reload --port 8000`
- dev 数据范围：nav_daily/perform_abs 仅 2025-12；持仓/资产配置/分类 3 个季度截面；行业/概念 2 个截面
