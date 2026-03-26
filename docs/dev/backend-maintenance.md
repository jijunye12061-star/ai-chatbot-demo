# 后端维护指南

## 整体架构速览

```
用户问题
  → orchestrator.py（入口）
  → MainAgent（agents/main_agent.py）
  → BaseAgent FC 循环（调工具 → 继续 → 流式输出）
```

所有意图（数据查询 / 基金筛选 / 报告生成 / 闲聊）都走同一个 MainAgent，无路由分叉。

---

## 新增场景的三种情况

### 情况一：新增数据查询（新表或新指标）

**不改代码，只加文档和数据。**

1. 数据库建表，同步更新 `data/schema_mysql.sql`
2. `templates/table_catalog.md` — 追加一行（表名 + 一句描述）
3. `templates/table_specs/新表名.md` — 写字段清单、枚举值、查询示例
4. `data/test_chat.py` — 加一个测试问题验证

> AI 会自动读目录，按需加载表规格，自己写 SQL。

---

### 情况二：新增复杂筛选场景（需要业务逻辑指引）

在情况一基础上额外加：

5. `templates/screen_catalog.md` — 追加索引一行
6. `templates/screen_guides/新场景.md` — 写 SQL 写法知识文档（CTE 结构、枚举规则等）

> 参考已有的 `industry_exposure.md` / `performance_filter.md` 的格式。

---

### 情况三：新增全新能力（工具级别）

**需要改代码，按顺序操作：**

1. `tools/新工具.py` — 实现工具函数（async，返回 dict 或 str）
2. `tools/definitions.py` — 注册 JSON Schema（参考已有 5 个工具格式）
3. `tools/registry.py` — 加入注册映射
4. `prompts/main_agent.md` — 在 prompt 里说明何时调用此工具
5. `tests/` — 加单测

> 如需子 Agent，参考 `agents/report_agent.py` + `tools/report_agent_bridge.py` 的模式。

---

## 关键文件速查

| 文件 | 作用 |
|------|------|
| `prompts/main_agent.md` | 主 prompt，含表目录和筛选目录占位符 |
| `templates/table_catalog.md` | 9 张表的极简索引（始终注入） |
| `templates/table_specs/*.md` | 每张表的详细规格（按需加载） |
| `templates/screen_catalog.md` | 筛选场景索引（始终注入） |
| `templates/screen_guides/*.md` | 筛选知识文档（按需加载） |
| `db/safety.py` | SQL 安全校验，白名单从 `table_specs/` 文件名自动读取 |

---

## 常见注意事项

- **新表加白名单**：只需在 `templates/table_specs/` 下建文件，`safety.py` 会自动把文件名加入 SQL 白名单，不用手动改代码。
- **dev 环境缺表**：`tb_fd_tag_asset_fi` / `tb_fd_tag_asset_mix` 在 dev 无表，测试时跳过涉及这两张表的场景。
- **数据范围**：dev 数据 nav_daily/perform_abs 仅 2025-12，持仓/资产配置/分类 3 个季度截面。
- **测试**：改完用 `cd backend && python -m pytest tests/ -v` 跑单测，再用 `data/test_chat.py` 跑端到端验证。
