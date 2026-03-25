# 行业曝露度筛选（申万 / 中信）

适用场景：用户想找"重仓某行业的基金"，如"重仓电子行业的权益基金"、"同时配了半导体和面板的基金"。

## 涉及的表
- `tb_fd_portfolio_stk` — 基金持仓明细
- `tb_stk_industry` — 股票行业归属（`c_sw_code` 申万, `c_citic_code` 中信, `c_trade_date`）
- `tb_fd_category` — 基金分类
- `tb_fd_basic_info` — 基金基础信息

## 行业分类选择

`tb_stk_industry` 同时提供申万和中信两套分类：

| 分类 | 字段 | 一级码示例 | 维度查询 |
|------|------|----------|---------|
| 申万（2021） | `c_sw_code` | `029005`（电子） | `get_dimension_list('申万行业分类')` |
| 中信（2020） | `c_citic_code` | `025026`（电子） | `get_dimension_list('中信行业分类')` |

**判断规则**：
- 用户明确说"中信行业"→ 用 `c_citic_code`
- 其他情况（含模糊表达）→ **默认用申万** `c_sw_code`

## 行业码层级与匹配方式

两套分类均为四级结构（根/一/二/三级），码长依次为 3/6/9/12 位：

| 层级 | 码长 | 申万示例 | 中信示例 | 匹配方式 |
|------|------|---------|---------|---------|
| 根（整套分类） | 3位 | `029` | `025` | 不用于筛选 |
| 一级 | 6位 | `029005`（电子） | `025026`（电子） | `LEFT(字段, 6) IN (...)` |
| 二级 | 9位 | `029005001`（半导体） | `025026001` | `LEFT(字段, 9) IN (...)` |
| 三级 | 12位 | `029005001001` | `025026001001` | `字段 IN (...)` |

支持混合层级：用 OR 连接不同长度的条件。

**需要先调用 `get_dimension_list('申万行业分类')` 或 `get_dimension_list('中信行业分类')` 获取完整码列表，再根据用户描述选出目标 code。**

## SQL 写法示例（以申万电子行业为例）

### Step A：获取日期

```sql
-- 最新持仓日期
SELECT MAX(c_report_date) AS latest_date FROM tb_fd_portfolio_stk;

-- 最近2期中报/年报日期
SELECT DISTINCT c_report_date
FROM tb_fd_portfolio_stk
WHERE c_style IN ('02', '04')
ORDER BY c_report_date DESC
LIMIT 2;
```

### Step B：最新期行业曝露度

```sql
SELECT p.c_fd_code,
       b.c_short_name,
       cat.c_type1_name,
       SUM(p.c_nav_ratio) AS latest_exposure
FROM (
    SELECT c_fd_code, c_report_date, c_stk_code,
           MIN(CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) AS best_prio
    FROM tb_fd_portfolio_stk
    WHERE c_report_date = '2025-12-31'  -- 替换为 Step A 查到的日期
    GROUP BY c_fd_code, c_report_date, c_stk_code
) best
JOIN tb_fd_portfolio_stk p
  ON p.c_fd_code = best.c_fd_code
  AND p.c_stk_code = best.c_stk_code
  AND p.c_report_date = best.c_report_date
  AND (CASE p.c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) = best.best_prio
JOIN tb_stk_industry si
  ON p.c_stk_code = si.c_stk_code
  AND p.c_report_date = si.c_trade_date
  AND (
    LEFT(si.c_sw_code, 6) IN ('029005')       -- 申万一级：电子
    -- 中信示例: LEFT(si.c_citic_code, 6) IN ('025026')
    -- 混合层级: OR LEFT(si.c_sw_code, 9) IN ('029005001')
  )
LEFT JOIN (
    SELECT c_fd_code, c_type1_code, c_type1_name, c_type2_name,
           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
    FROM tb_fd_category
) cat ON p.c_fd_code = cat.c_fd_code AND cat.rn = 1
JOIN tb_fd_basic_info b ON p.c_fd_code = b.c_fd_code
WHERE p.c_report_date = '2025-12-31'
  AND cat.c_type1_code = '001'   -- 可选：限定权益基金
GROUP BY p.c_fd_code, b.c_short_name, cat.c_type1_name
HAVING SUM(p.c_nav_ratio) >= 5
ORDER BY latest_exposure DESC
LIMIT 50;
```

### Step C：历史期行业曝露度

逻辑同概念筛选的 Step C，将 `tb_stk_concept sc` 替换为 `tb_stk_industry si`，
将 `sc.c_concept_code IN (...)` 替换为行业码的 OR 条件。

```sql
SELECT p2.c_fd_code, p2.c_report_date, SUM(p2.c_nav_ratio) AS exposure
FROM (
    SELECT c_fd_code, c_report_date, c_stk_code,
           MIN(CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) AS best_prio
    FROM tb_fd_portfolio_stk
    WHERE c_report_date IN ('2025-06-30', '2025-12-31')  -- 替换为 Step A 查到的历史日期
      AND c_style IN ('02', '04')
    GROUP BY c_fd_code, c_report_date, c_stk_code
) best2
JOIN tb_fd_portfolio_stk p2
  ON p2.c_fd_code = best2.c_fd_code
  AND p2.c_stk_code = best2.c_stk_code
  AND p2.c_report_date = best2.c_report_date
  AND (CASE p2.c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) = best2.best_prio
JOIN tb_stk_industry si2
  ON p2.c_stk_code = si2.c_stk_code
  AND p2.c_report_date = si2.c_trade_date
  AND LEFT(si2.c_sw_code, 6) IN ('029005')
WHERE p2.c_style IN ('02', '04')
GROUP BY p2.c_fd_code, p2.c_report_date;
```

然后在应用层（或嵌套查询）按基金取各期均值，筛选 >= 阈值的基金。

## 关键注意事项

1. **分类选择**：默认申万（`c_sw_code`），用户明确说中信时用 `c_citic_code`
2. **行业码长度决定匹配方式**：6位用 `LEFT(...,6)`，9位用 `LEFT(...,9)`，12位直接 `IN`
3. **多行业 OR 逻辑**：用括号包裹所有行业条件
4. **行业截面日 = 持仓报告日**：`p.c_report_date = si.c_trade_date`
5. **dev 环境限制**：`tb_stk_industry` 只有 2025-09-30 和 2025-12-31 两个截面，历史期查询结果稀少属正常
