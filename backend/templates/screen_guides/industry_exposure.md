# 申万行业曝露度筛选

适用场景：用户想找"重仓某行业的基金"，如"重仓电子行业的权益基金"、"同时配了半导体和面板的基金"。

## 涉及的表
- `tb_fd_portfolio_stk` — 基金持仓明细
- `tb_stk_industry` — 股票申万行业归属（c_stk_code, c_sw_code, c_trade_date）
- `tb_fd_category` — 基金分类
- `tb_fd_basic_info` — 基金基础信息

## 行业码说明（申万三级体系）

| 层级 | 码长 | 示例 | 匹配方式 |
|------|------|------|---------|
| 一级 | 6位 | 330000（电子） | `LEFT(c_sw_code, 6) IN (...)` |
| 二级 | 9位 | 330100（半导体） | `LEFT(c_sw_code, 9) IN (...)` |
| 三级 | 12位 | 330101001（存储芯片） | `c_sw_code IN (...)` |

支持混合层级：用 OR 连接不同长度的条件。

**需要先调用 `get_dimension_list('申万行业分类')` 获取完整码列表，再根据用户描述选出目标 code。**

## SQL 写法示例

### Step A：获取日期（同概念筛选）

```sql
SELECT MAX(c_report_date) AS latest_date FROM tb_fd_portfolio_stk;

SELECT DISTINCT c_report_date
FROM tb_fd_portfolio_stk
WHERE c_style IN ('02', '04')
ORDER BY c_report_date DESC
LIMIT 2;
```

### Step B：最新期行业曝露度（混合层级示例：一级330000 + 二级330100）

```sql
SELECT p.c_fd_code,
       b.c_short_name,
       cat.c_type1_name,
       SUM(p.c_nav_ratio) AS latest_exposure
FROM (
    SELECT c_fd_code, c_report_date, c_stk_code,
           MIN(CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) AS best_prio
    FROM tb_fd_portfolio_stk
    WHERE c_report_date = '2025-12-31'
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
    LEFT(si.c_sw_code, 6) IN ('330000')      -- 一级行业
    OR LEFT(si.c_sw_code, 9) IN ('330100')   -- 二级行业
    -- 三级行业: si.c_sw_code IN ('330101001')
  )
LEFT JOIN (
    SELECT c_fd_code, c_type1_code, c_type1_name, c_type2_name,
           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
    FROM tb_fd_category
) cat ON p.c_fd_code = cat.c_fd_code AND cat.rn = 1
JOIN tb_fd_basic_info b ON p.c_fd_code = b.c_fd_code
WHERE p.c_report_date = '2025-12-31'
  AND cat.c_type1_code = '001'   -- 可选：限定基金类型
GROUP BY p.c_fd_code, b.c_short_name, cat.c_type1_name
HAVING SUM(p.c_nav_ratio) >= 5
ORDER BY latest_exposure DESC
LIMIT 50;
```

### Step C：历史期行业曝露度

逻辑同概念筛选的 Step C，将 `tb_stk_concept sc` 替换为 `tb_stk_industry si`，
将 `sc.c_concept_code IN (...)` 替换为行业码的 OR 条件。

## 关键注意事项

1. **行业码长度决定匹配方式**：6位用 LEFT(...,6)，9位用 LEFT(...,9)，12位直接 IN
2. **多行业 OR 逻辑**：用括号包裹所有行业条件，`( LEFT(...,6) IN (...) OR LEFT(...,9) IN (...) )`
3. **行业截面日 = 持仓报告日**：`p.c_report_date = si.c_trade_date`
4. **dev 环境限制**：tb_stk_industry 只有 2025-09-30 和 2025-12-31 两个截面
