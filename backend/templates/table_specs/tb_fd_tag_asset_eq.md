# tb_fd_tag_asset_eq — 权益基金资产配置标签表

**主键**: (c_fd_code, c_report_date) | **更新频率**: 季度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_report_date | DATE | 报告期（季度截止日） |
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_stk_pos_avg | DECIMAL(8,4) | 股票仓位均值（近八期均值，**单位：%**，85.5=85.5%） |
| c_stk_pos_chg_avg | DECIMAL(8,4) | 股票仓位变动均值（近八期均值，**单位：%**） |
| c_stk_pos_level | VARCHAR(20) | 仓位等级（见枚举） |
| c_stk_timing | VARCHAR(10) | 择时标签（见枚举） |
| c_updatetime | DATETIME(3) | 更新时间 |

## 注意事项

- **仅覆盖权益基金**（对应 tb_fd_category 中 c_type1_code = '001' 的基金）
- c_stk_pos_avg 和 c_stk_pos_chg_avg **单位是 %**，85.5 表示 85.5%
- 本地数据时间范围：c_report_date 有 3 个截面：2025-06-30 / 2025-09-30 / 2025-12-31
- CSV 导入后空值为空字符串

## 枚举值

### 仓位等级（c_stk_pos_level）
| 取值 | 判断逻辑 |
|------|----------|
| 高仓位 | 股票仓位均值 ≥ 90% |
| 中高仓位 | 股票仓位均值 < 90% |

### 择时标签（c_stk_timing）
| 取值 | 判断逻辑 |
|------|----------|
| 择时 | 仓位变动均值 ≥ 5% |
| 不择时 | 仓位变动均值 < 5% |

## 常用查询示例

```sql
-- 查询某基金最新仓位标签
SELECT c_fd_code, c_report_date,
       c_stk_pos_avg, c_stk_pos_level, c_stk_timing
FROM tb_fd_tag_asset_eq
WHERE c_fd_code = '000001'
ORDER BY c_report_date DESC
LIMIT 1;

-- 查询高仓位且择时的权益基金（最新截面）
SELECT t.c_fd_code, b.c_short_name, b.c_company_name,
       t.c_stk_pos_avg, t.c_stk_pos_level, t.c_stk_timing
FROM tb_fd_tag_asset_eq t
JOIN tb_fd_basic_info b ON t.c_fd_code = b.c_fd_code
WHERE t.c_report_date = '2025-09-30'
  AND t.c_stk_pos_level = '高仓位'
  AND t.c_stk_timing = '择时'
ORDER BY t.c_stk_pos_avg DESC
LIMIT 20;

-- 统计各仓位等级、择时标签的基金数量
SELECT c_stk_pos_level, c_stk_timing, COUNT(*) AS cnt
FROM tb_fd_tag_asset_eq
WHERE c_report_date = '2025-09-30'
GROUP BY c_stk_pos_level, c_stk_timing
ORDER BY cnt DESC
LIMIT 10;
```
