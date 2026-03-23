# AI 问答系统

## 聊天界面

- 输入框 + 发送按钮，Enter 发送 / Shift+Enter 换行
- 消息气泡（用户右侧、AI 左侧）
- AI 回答支持 Markdown 渲染（代码块、表格、加粗等），流式输出期间显示原文防闪烁
- 流式打字机效果：逐字显示，非等全部生成完再展示
- 自动滚动到最新消息
- 建议问题卡片（首屏空状态）
- 多轮对话：`history` 由前端维护，每轮对话追加后传给后端（后端无状态）

---

## 多 Agent 架构

```
用户输入
  → Orchestrator
    → RouterAgent（意图识别）
      ├── chat       → ChatAgent（闲聊，直接流式输出）
      ├── data_query → DataQueryAgent（SQL 查询 + 两层召回）
      ├── fund_screen→ FundScreenerAgent（模板填参筛选）
      └── report     → ReportAgent（并行生成多节报告）
```

### RouterAgent

- 使用 Function Calling（`route_to` tool）保证结构化返回
- 降级策略：LLM tool_call → 文本解析 → 关键词匹配 → 默认 chat

### DataQueryAgent（数据查询）

两层召回架构：
1. LLM 先看 `table_catalog.md`（极简目录）决定需要哪些表
2. 调用 `get_table_schema` 工具按需加载详细字段说明
3. 生成 SQL → 安全校验 → 只读执行

### FundScreenerAgent（基金筛选）

模板填参架构：
1. LLM 从 `screen_catalog.md` 选择最合适的筛选模板
2. 调用 `run_screen_template` 工具，传入模板 ID + 参数
3. 工具内部完成参数校验、SQL 渲染、执行

新增筛选场景只需在 `backend/templates/screen_templates/` 下添加 YAML 模板。

### ReportAgent（报告生成）

- 按 `fund_report.json` 模板定义，分节并行生成（`asyncio.gather`）
- 各节有独立的 prompt 文件（`prompts/report_*.md`）

---

## SQL 安全机制

`backend/db/safety.py` 对 LLM 生成的 SQL 做多层校验：

1. 去除注释（防注释注入）
2. 禁止危险关键词（DROP / DELETE / UPDATE 等）
3. 禁止多语句（分号检测）
4. 只允许 SELECT 语句
5. 表名白名单（从 `table_specs/` 目录自动读取）
6. 子查询深度 ≤ 2
7. 自动注入 LIMIT（缺失时补上，上限 1000 行）

---

## Phase 3：AI → 模型页面联动

AI 在回答时调用 `recommend_model` tool，前端将工具结果渲染为可点击的跳转卡片。

```json
{
  "tool": "recommend_model",
  "model_id": "yield-curve",
  "display_name": "收益率曲线模型",
  "reason": "您可以查看最新的收益率曲线走势"
}
```
