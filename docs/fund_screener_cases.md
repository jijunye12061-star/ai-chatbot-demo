# 基金筛选问题池

记录基金筛选功能的典型用户提问、期望路径和测试状态。

---

## 场景一：主题/概念筛选

### Case 1.1 — 概念板块持仓筛选
- **用户提问示例**：筛选持有新能源汽车概念股较多的权益基金
- **期望路径**：get_dimension_list('概念板块') → 选出新能源汽车相关 code → get_screen_guide('concept_exposure') → AI 写 SQL → execute_sql
- **关键参数**：concept_codes=[...], min_latest_exposure=5（在 SQL 中体现）
- **状态**：已实现

### Case 1.2 — 申万行业持仓筛选
- **用户提问示例**：哪些基金重仓了申万一级行业中的电子行业？
- **期望路径**：get_dimension_list('申万行业分类') → 选出电子行业6位码 → get_screen_guide('industry_exposure') → AI 写 SQL → execute_sql
- **关键参数**：sw_codes=['330000'（示例）], min_latest_exposure=10（在 SQL 中体现）
- **状态**：已实现

### Case 1.3 — 多级行业混合筛选
- **用户提问示例**：帮我筛一下同时配了半导体和面板的基金
- **期望路径**：get_dimension_list → 分别找半导体（二级/三级）和面板的码 → get_screen_guide('industry_exposure') → AI 写 SQL（多 LIKE 匹配）→ execute_sql
- **关键参数**：sw_codes=[多个不同长度的码]
- **状态**：已实现

---

## 场景二：多条件业绩筛选

### Case 2.1 — 单区间多指标筛选
- **用户提问示例**：近1年年化收益>10%且最大回撤<20%的权益基金有哪些？
- **期望路径**：get_screen_guide('performance_filter') → AI 写 SQL（单区间 WHERE 条件）→ execute_sql
- **关键参数**：fund_category_code='权益基金'，条件在 SQL WHERE 子句中体现
- **状态**：已实现

### Case 2.2 — 跨区间多条件筛选
- **用户提问示例**：近3月最大回撤<10%，同时近1年年化收益>20%的权益基金有哪些？
- **期望路径**：get_screen_guide('performance_filter') → AI 写 SQL（多区间动态 JOIN）→ execute_sql
- **关键参数**：多区间条件，SQL 需多次 JOIN tb_fd_perform_abs
- **状态**：已实现

### Case 2.3 — 全类型扫描
- **用户提问示例**：近3月表现最好的基金有哪些？（不限类型）
- **期望路径**：get_screen_guide('performance_filter') → AI 写 SQL（不加 fund_category 过滤）→ execute_sql
- **关键参数**：无类型过滤，ORDER BY 业绩指标
- **状态**：已实现

### Case 2.4 — 逐年达标
- **用户提问示例**：最近3年每年年化收益都超过8%的基金有哪些？
- **期望路径**：get_table_schema('tb_fd_perform_abs') → AI 自写 SQL（多年达标逻辑）→ execute_sql
- **关键参数**：N/A（SQL 由 MainAgent 直接生成）
- **状态**：已实现（MainAgent 直接写 SQL 路径）

---

## 场景三：资产配置标签筛选

### Case 3.1 — 权益基金仓位标签
- **用户提问示例**：哪些权益基金属于高仓位且主动择时的？
- **期望路径**：get_screen_guide('tag_equity') → AI 写 SQL（WHERE c_stk_pos_level=... AND c_stk_timing=...）→ execute_sql
- **状态**：已实现

### Case 3.2 — 固收+基金风险标签
- **用户提问示例**：有哪些稳健型固收+基金？
- **期望路径**：get_screen_guide('tag_fixed_income') → AI 写 SQL（WHERE c_eq_risk_level=...）→ execute_sql
- **状态**：已实现（dev 环境 tb_fd_tag_asset_fi 不存在，生产可用）

### Case 3.3 — 混合基金股债偏好
- **用户提问示例**：偏股型混合基金里有哪些择时能力强的？
- **期望路径**：get_screen_guide('tag_mixed') → AI 写 SQL（WHERE c_stk_bd_pref=... AND c_eq_timing=...）→ execute_sql
- **状态**：已实现（dev 环境 tb_fd_tag_asset_mix 不存在，生产可用）

---

## 待扩展场景（后续设计）

- 指数成分股筛选（如沪深300成分基金）— 复杂度高，后续单独设计
- 基金经理历史业绩筛选 — 需要添加相关表
- 同类排名百分位筛选 — 需要计算分位数
