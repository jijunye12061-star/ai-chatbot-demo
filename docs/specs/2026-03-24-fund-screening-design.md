# 基金筛选功能设计文档

**日期**：2026-03-24
**状态**：待实施
**作者**：brainstorming session

---

## 1. 背景与目标

当前 FundScreenerAgent 仅有模板001（区间收益率排名）。本次设计扩展基金筛选能力，覆盖三类核心场景：

| 场景 | 描述 |
|------|------|
| 主题/概念筛选 | 筛选对某概念板块或申万行业有显著持仓曝露的基金 |
| 多条件业绩筛选 | 按年化收益、最大回撤、夏普比率等指标组合过滤 |
| 资产配置标签筛选 | 按仓位等级、择时标签、风险特征等枚举标签过滤 |

**不在本次范围内**：逐年达标类查询（如"最近3年每年年化>8%"），走 DataQueryAgent + LLM 自写 SQL，在 `tb_fd_perform_abs` table spec 补充示例 case 即可。

---

## 2. 整体架构

### 2.1 路由设计

所有基金筛选问题统一路由到 FundScreenerAgent，不要求 RouterAgent 区分"模板能否覆盖"：

```
用户提问
  → RouterAgent → fund_screen 意图
    → FundScreenerAgent（FC Loop）
        ① get_dimension_list()    可选，概念/行业码召回
        ② run_screen_template()   模板覆盖的场景
        ③ ask_data_agent()        模板覆盖不了时委托 DataQueryAgent
```

**职责边界**：
- FundScreenerAgent：只知道筛选模板和参数，不感知数据库 schema
- DataQueryAgent：持有完整 table catalog，处理任意 SQL 查询
- `ask_data_agent` 工具：同进程内异步调用 DataQueryAgent，FundScreenerAgent 拿结果后组织回答

### 2.2 新增工具

| 工具 | 文件 | 函数签名 | 用途 |
|------|------|---------|------|
| `get_dimension_list` | `tools/dimension_lookup.py` | `def get_dimension_list(dim_type: str) -> str` | 全量拉取概念板块/行业分类码+名称+描述，LLM 读取后选出匹配的码 |
| `ask_data_agent` | `tools/data_agent_bridge.py` | `async def ask_data_agent(question: str) -> str` | 将子问题委托给 DataQueryAgent（必须声明为 async def，内部通过 async for 收集所有 chunk 后拼接返回） |

**`get_dimension_list` 返回格式**：JSON 字符串，数组，每条包含 `{code, name, parent_code, remark}`（remark 仅概念板块有值，行业分类为空字符串）。不设条数上限，返回指定 `dim_type` 的全量记录。

**`ask_data_agent` 实现要点**：内部实例化 DataQueryAgent 并调用其 run 方法，`async for` 收集所有流式 chunk 拼接成完整字符串后返回。DataQueryAgent 独立加载自己的 table_catalog + schema 工具，FundScreenerAgent 不感知任何表结构细节。

### 2.3 问题池工作流

维护 `docs/fund_screener_cases.md`，格式：

```markdown
## 场景标题
- 用户提问示例：...
- 期望路径：模板XXX / DataQuery
- 关键参数：...
- 状态：待实现 / 已测试 / 已上线
```

初期批次（本次设计）覆盖3类场景的基础模板。后续新增场景时：用户更新 cases 文件 → 输出解法分析 → 确认后实现 YAML + 代码。

---

## 3. 模板系统改造（fund_filter.py）

### 3.1 YAML 占位符格式升级

旧格式（硬编码 `%s` 顺序）升级为**具名占位符**：

| 占位符 | 类型 | 展开规则 |
|--------|------|---------|
| `{:param_name}` | 标量（string/int/float/date/enum） | → `%s`，值追加到 params |
| `{*param_name}` | list | → `IN (%s, %s, ...)` 含 `IN` 关键字，按列表长度展开，值逐一追加。YAML sql 中写 `col {*x}` 即可，不需要额外写 `IN` |
| `{?param_name}` | 可选 WHERE 片段 | 有值 → 按 param_defs 中 `fragment` 字段展开（含 `%s`），params 追加值（通配符 `%value%` 由 Python 层处理，与模板001保持一致）；无值 → `1=1` |
| `{@conditions}` | conditions 字典 | 遍历字典，按 min/max 动态拼 `AND field >= %s` / `AND field <= %s`，字段名做白名单校验 |
| `{#sw_industry}` | 行业码多级匹配（模板003专用） | 按传入码列表中每个码的长度动态生成 `LEFT(c_sw_code, N) IN (...)` 片段，各级取 OR 合并 |

### 3.2 `_build_and_execute_sql` 重构

拆为两步：

**`_render_sql(sql_template, param_defs, validated_params) → (rendered_sql, params_tuple)`**

```
扫描 sql_template 中的占位符：
  {:x}   → 替换为 %s，params += [validated[x]]
  {*x}   → 替换为 IN (%s,...) n个，params += validated[x] 列表元素
  {?x}   → 有值：替换为 param_defs[x].fragment（含 %s），params += [值（必要时加 %通配符%）]
            无值：替换为 1=1
  {@x}   → 遍历 conditions 字典：
            field 必须在 ALLOWED_CONDITION_FIELDS 白名单中（防注入）
            min 非 null → AND field >= %s，params += [min]
            max 非 null → AND field <= %s，params += [max]
  {#sw_industry} → 按码长度分组，生成
            (LEFT(c_sw_code,6) IN (%s,...) OR LEFT(c_sw_code,9) IN (%s,...) OR c_sw_code IN (%s,...))
            各组分别追加 params
            边界处理：
            - sw_codes 为空列表 → 展开为 1=0（合法 SQL，返回空结果，避免语法错误）
            - 码长度非 6/9/12 位 → _render_sql 抛出 ValueError 说明原因，不静默跳过
```

**`_validate_params` 需新增类型处理分支**：

- `conditions` 类型：遍历字典 key，对照 `ALLOWED_CONDITION_FIELDS` 白名单校验字段名，value 的 min/max 转 float（null 保留为 None）
- `dict` 类型（tag_conditions）：遍历字典 key，对照 YAML 中 `allowed_tag_fields` 列表校验字段名，拒绝不在白名单中的字段（防止字段名注入）

**`ALLOWED_CONDITION_FIELDS` 全局白名单**（`fund_filter.py` 顶层常量）：

```python
ALLOWED_CONDITION_FIELDS = {
    "c_ann_ret", "c_period_ret", "c_mdd", "c_sharpe",
    "c_calmar", "c_sortino", "c_ann_vol", "c_break_ratio"
}
```

模板001同步迁移到新占位符格式，保持功能不变。

### 3.3 db/safety.py 子查询深度调整

当前 `_subquery_depth` 限制为 2 层。模板002 使用三层 CTE（含内嵌派生表），需将深度限制调整为 **4**。模板 SQL 为人工编写（非 LLM 生成），安全校验的目的是防意外篡改，深度放宽合理。

---

## 4. 新增模板详细设计

### 模板002 — 概念主题曝露度筛选

**文件**：`templates/screen_templates/002_concept_exposure.yaml`

**数据逻辑**：
- 持仓曝露度 = `SUM(c_nav_ratio)`（字段本身已是占净值 %），无需除法
- **报告期去重规则**：同一 `c_report_date` 下，年报（`c_style='04'`）优先于四季报（`c_style='06'`）。用 `ROW_NUMBER() OVER (PARTITION BY c_fd_code, c_report_date ORDER BY CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END)` 去重取 rn=1。此去重规则在最新一期（`latest_dedup` CTE）和历史口径（`hist_dedup` CTE）均需应用。
- **历史口径**：在去重后的数据中，筛选 `c_style IN ('02', '04')`（半年报 + 年报），取最近两个报告期。**注意**：若某报告期实际只有四季报（年报未生成），去重后 `rn=1` 的行 `c_style='06'`，此时 `AND c_style IN ('02','04')` 会过滤该报告期——这是业务决策（历史口径刻意只取全部持仓披露期），符合预期
- **dev 环境注意**：`tb_stk_concept` 仅有两个截面（2025-09-30 / 2025-12-31），持仓表 2025-06-30 截面与概念表 INNER JOIN 后该截面数据会因无匹配而静默丢失，属 dev 数据限制，prod 环境正常

**参数**：

```yaml
params:
  concept_codes:
    type: list
    description: 概念板块代码列表，由 get_dimension_list + LLM 选定
    required: true

  min_latest_exposure:
    type: float
    description: 最新一期概念曝露度下限（%），默认5，降序排列后用户可自行判断
    required: false
    default: 5

  min_hist_exposure:
    type: float
    description: 近两期半年/年报曝露度均值下限（%）
    required: false
    default: 5

  fund_category:
    type: string
    description: |
      一级分类名称过滤（可选），如"权益基金"；有值时展开为 AND cat.c_type1_name LIKE %s，Python层加%通配符%。
      注意：cat 为 LEFT JOIN，无分类记录的基金 cat 字段为 NULL，LIKE 条件结果为 NULL，该基金会被过滤——
      这是预期行为（无分类基金不纳入按类型筛选的结果）。
    required: false

  limit:
    type: int
    default: 50
    max: 200
```

**SQL 结构**（CTE 四层）：

```sql
WITH all_dedup AS (
  -- 所有报告期去重：同日期年报优先于四季报
  SELECT c_fd_code, c_report_date, c_style, c_stk_code, c_nav_ratio,
         ROW_NUMBER() OVER (
           PARTITION BY c_fd_code, c_report_date
           ORDER BY CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END
         ) AS rn
  FROM tb_fd_portfolio_stk
),
latest_exp AS (
  -- 最新一期曝露度（任意 c_style，去重后取最新报告期）
  SELECT p.c_fd_code,
         SUM(p.c_nav_ratio) AS latest_exposure
  FROM all_dedup p
  JOIN tb_stk_concept sc
    ON p.c_stk_code = sc.c_stk_code
    AND p.c_report_date = sc.c_trade_date
    AND sc.c_concept_code {*concept_codes}
  WHERE p.rn = 1
    AND p.c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_portfolio_stk)
  GROUP BY p.c_fd_code
  HAVING latest_exposure >= {:min_latest_exposure}
),
hist_exp AS (
  -- 近两期半年/年报曝露度均值（去重后取半年报+年报两期）
  SELECT period_exp.c_fd_code,
         AVG(period_exp.exposure) AS hist_exposure
  FROM (
    SELECT p2.c_fd_code, p2.c_report_date,
           SUM(p2.c_nav_ratio) AS exposure
    FROM all_dedup p2
    JOIN tb_stk_concept sc2
      ON p2.c_stk_code = sc2.c_stk_code
      AND p2.c_report_date = sc2.c_trade_date
      AND sc2.c_concept_code {*concept_codes}
    WHERE p2.rn = 1
      AND p2.c_style IN ('02', '04')
      AND p2.c_report_date IN (
        SELECT DISTINCT c_report_date FROM tb_fd_portfolio_stk
        WHERE c_style IN ('02', '04')
        ORDER BY c_report_date DESC LIMIT 2
      )
    GROUP BY p2.c_fd_code, p2.c_report_date
  ) period_exp
  GROUP BY period_exp.c_fd_code
  HAVING hist_exposure >= {:min_hist_exposure}
)
SELECT b.c_fd_code, b.c_short_name,
       cat.c_type1_name, cat.c_type2_name,
       le.latest_exposure, he.hist_exposure
FROM latest_exp le
JOIN hist_exp he ON le.c_fd_code = he.c_fd_code
JOIN tb_fd_basic_info b ON le.c_fd_code = b.c_fd_code
LEFT JOIN (
    SELECT c_fd_code, c_type1_name, c_type2_name,
           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
    FROM tb_fd_category
) cat ON b.c_fd_code = cat.c_fd_code AND cat.rn = 1
{?fund_category}
ORDER BY le.latest_exposure DESC
LIMIT {:limit}
```

---

### 模板003 — 申万行业曝露度筛选

**文件**：`templates/screen_templates/003_industry_exposure.yaml`

**与002的差异**：
- JOIN `tb_stk_industry` 而非 `tb_stk_concept`
- 行业码匹配使用 `{#sw_industry}` 占位符，`_render_sql` 按传入码的实际长度分组：
  - 6位 → `LEFT(c_sw_code, 6) IN (%s, ...)`（一级行业）
  - 9位 → `LEFT(c_sw_code, 9) IN (%s, ...)`（二级行业）
  - 12位 → `c_sw_code IN (%s, ...)`（三级行业）
  - 多组之间取 OR，整体用括号包裹
- `get_dimension_list('申万行业分类')` 返回字段含 `parent_code`，LLM 可展开大板块（如"中游制造"→多个二级行业码）

**参数**：

```yaml
params:
  sw_codes:
    type: list
    description: 申万行业代码列表（支持一/二/三级混合，按代码长度自动匹配）
    required: true
  min_latest_exposure:
    type: float
    default: 5
  min_hist_exposure:
    type: float
    default: 5
  fund_category:
    type: string
    required: false
  limit:
    type: int
    default: 50
    max: 200
```

**SQL 结构**（与002相同的 CTE 四层结构，JOIN 表和匹配条件不同）：

```sql
WITH all_dedup AS (
  -- 同002：年报优先去重
  ...
),
latest_exp AS (
  SELECT p.c_fd_code, SUM(p.c_nav_ratio) AS latest_exposure
  FROM all_dedup p
  JOIN tb_stk_industry si
    ON p.c_stk_code = si.c_stk_code
    AND p.c_report_date = si.c_trade_date
    AND ({#sw_industry})   -- 展开为 LEFT(c_sw_code,6) IN(...) OR LEFT(c_sw_code,9) IN(...)
  WHERE p.rn = 1
    AND p.c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_portfolio_stk)
  GROUP BY p.c_fd_code
  HAVING latest_exposure >= {:min_latest_exposure}
),
hist_exp AS (
  -- 同002结构，JOIN tb_stk_industry
  ...
)
SELECT ... ORDER BY le.latest_exposure DESC LIMIT {:limit}
```

> dev 环境注意：`tb_stk_industry` 同样只有两个截面，2025-06-30 持仓截面会因无匹配而丢失，与002相同。

---

### 模板004 — 单期多条件业绩筛选

**文件**：`templates/screen_templates/004_performance_filter.yaml`

**参数**：

```yaml
params:
  period_code:
    type: enum
    required: true
    options:
      近1月: "00"
      近3月: "01"
      近6月: "02"
      近1年: "03"
      近2年: "04"
      近3年: "05"
      近5年: "06"
      年初至今: "07"
      成立以来: "08"

  fund_category:
    type: string
    description: 一级分类名称，默认"权益基金"；有值时展开为 AND cat.c_type1_name LIKE %s，Python层加%通配符%
    required: false
    default: "权益基金"

  conditions:
    type: conditions
    description: |
      指标约束字典，格式 {字段名: {min: 数值或null, max: 数值或null}}
      可用字段（白名单）：c_ann_ret, c_period_ret, c_mdd, c_sharpe,
                         c_calmar, c_sortino, c_ann_vol, c_break_ratio
      示例：{c_ann_ret: {min: 8, max: null}, c_mdd: {min: null, max: 15}}
    required: false

  limit:
    type: int
    default: 20
    max: 200
```

**多类型输出说明**（写入 `prompts/fund_screener.md`）：

> 若用户未指定基金类型，对权益基金/固收加基金/债券基金/混合基金分别调用模板004一次（共四次 tool call），合并结果按类型分组展示。

**SQL 结构**：

```sql
SELECT b.c_fd_code, b.c_short_name,
       cat.c_type1_name, cat.c_type2_name,
       p.c_ann_ret, p.c_mdd, p.c_sharpe, p.c_calmar, p.c_period_ret
FROM tb_fd_perform_abs p
JOIN tb_fd_basic_info b ON p.c_fd_code = b.c_fd_code
LEFT JOIN (
    SELECT c_fd_code, c_type1_name, c_type2_name,
           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
    FROM tb_fd_category
) cat ON b.c_fd_code = cat.c_fd_code AND cat.rn = 1
WHERE p.c_trade_date = (SELECT MAX(c_trade_date) FROM tb_fd_perform_abs)
  AND p.c_period_code = {:period_code}
  {?fund_category}
  {@conditions}
ORDER BY p.c_ann_ret DESC
LIMIT {:limit}
```

---

### 模板005/006/007 — 资产配置标签筛选

**文件**：`005_tag_eq.yaml` / `006_tag_fi.yaml` / `007_tag_mix.yaml`

三个独立模板，避免动态表名。`tag_conditions` 字段名做白名单校验（per-template 在 YAML 中声明 `allowed_tag_fields`，`_validate_params` 对 dict 类型参数按此列表校验，拒绝不在白名单中的字段）。

```yaml
params:
  tag_conditions:
    type: dict
    description: "{字段名: 枚举值}，如 {c_stk_pos_level: '高仓位'}"
    required: true
    allowed_tag_fields: [c_stk_pos_level, c_stk_timing]  # 各模板不同
  limit:
    type: int
    default: 50
```

**各模板可用字段**：

| 模板 | 基金类型 | 查询表 | allowed_tag_fields |
|------|---------|-------|-------------------|
| 005_tag_eq | 权益基金 | tb_fd_tag_asset_eq | c_stk_pos_level, c_stk_timing |
| 006_tag_fi | 固收加基金 | tb_fd_tag_asset_fi | c_eq_risk_level, c_stk_cb_strategy, c_stk_timing, c_cb_timing |
| 007_tag_mix | 混合基金 | tb_fd_tag_asset_mix | c_stk_bd_pref, c_eq_strategy, c_eq_timing |

**screen_catalog 注入策略**：当前模板总数（001-007）较少，全部注入 screen_catalog.md 无需召回机制。后续模板增多时再考虑。

---

## 5. 涉及文件改动汇总

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `ARCHITECTURE.md` | 修改 | 新增/修改文件同步更新（优先更新） |
| `db/safety.py` | 修改 | `_subquery_depth` 限制从 2 调整为 4，支持模板002/003 的四层 CTE |
| `tools/fund_filter.py` | 重构 | `_build_and_execute_sql` → `_render_sql`（具名占位符 + list/conditions/dict/sw_industry 类型支持）；`_validate_params` 新增 conditions/dict 类型校验分支 |
| `tools/dimension_lookup.py` | 新增 | `get_dimension_list(dim_type: str) -> str` |
| `tools/data_agent_bridge.py` | 新增 | `async def ask_data_agent(question: str) -> str` |
| `tools/definitions.py` | 修改 | 新增 get_dimension_list 和 ask_data_agent 的 JSON Schema |
| `tools/registry.py` | 修改 | 注册新工具（`_lazy_register` 中 import 并调用 `register_tool`，名称需与下行 tool_names 一致） |
| `agents/fund_screener_agent.py` | 修改 | `tool_names` 列表加入 `get_dimension_list` 和 `ask_data_agent`（三处联动：definitions.py JSON Schema → registry.py 注册 → agent tool_names，缺一不可） |
| `prompts/fund_screener.md` | 修改 | 补充三类场景工作流说明、多类型四次调用说明、ask_data_agent 使用时机 |
| `templates/screen_templates/001_return_rank.yaml` | 修改 | 迁移到具名占位符格式 |
| `templates/screen_templates/002_concept_exposure.yaml` | 新增 | |
| `templates/screen_templates/003_industry_exposure.yaml` | 新增 | |
| `templates/screen_templates/004_performance_filter.yaml` | 新增 | |
| `templates/screen_templates/005_tag_eq.yaml` | 新增 | |
| `templates/screen_templates/006_tag_fi.yaml` | 新增 | |
| `templates/screen_templates/007_tag_mix.yaml` | 新增 | |
| `templates/screen_catalog.md` | 修改 | 更新模板目录（001-007） |
| `templates/table_specs/tb_fd_perform_abs.md` | 修改 | 补充逐年达标查询 case（DataQueryAgent 使用） |
| `templates/table_specs/tb_fd_tag_asset_fi.md` | 新增 | 模板006 依赖，SQL 白名单需要此文件存在 |
| `templates/table_specs/tb_fd_tag_asset_mix.md` | 新增 | 模板007 依赖，SQL 白名单需要此文件存在 |
| `tests/test_screen_template.py` | 修改 | `_render_sql` 重构是破坏性改动，原有12个 case 需验证仍通过；同时补充新占位符类型（list/conditions/dict）的测试 case |
| `tests/test_sql_safety.py` | 修改 | `_subquery_depth` 从2改为4后，原有"深度>2应拒绝"断言需更新为"深度>4应拒绝" |
| `docs/fund_screener_cases.md` | 新增 | 问题池文件 |

---

## 6. 不在本次范围内

- 向量 RAG（当前全量拉取 tb_dict_params 供 LLM 选择已足够）
- 指数成分股筛选（复杂度高，后续单独设计）
- 登录鉴权、对话持久化（Phase 1 已明确不做）
