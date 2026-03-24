# tb_fd_tag_asset_fi — 固收+基金资产配置标签表

**主键**: (c_report_date, c_fd_code) | **更新频率**: 季度 | **注意**: dev 环境暂无此表，生产环境可用

## 字段清单

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_report_date | DATE | 报告期（季报截止日） |
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_stk_pos_avg | DECIMAL(8,4) | 股票仓位均值（近八期均值，**单位：%**） |
| c_cb_pos_avg | DECIMAL(8,4) | 转债仓位均值（近八期均值，**单位：%**） |
| c_eq_pos_avg | DECIMAL(8,4) | 权益仓位均值（股票+转债/2，**单位：%**） |
| c_stk_pos_chg_avg | DECIMAL(8,4) | 股票仓位变动均值（**单位：%**） |
| c_cb_pos_chg_avg | DECIMAL(8,4) | 转债仓位变动均值（**单位：%**） |
| c_eq_risk_level | VARCHAR(10) | 风险特征标签（见枚举） |
| c_stk_cb_strategy | VARCHAR(30) | 股票转债策略标签（见枚举） |
| c_stk_timing | VARCHAR(10) | 股票择时标签（见枚举） |
| c_cb_timing | VARCHAR(10) | 转债择时标签（见枚举） |
| c_updatetime | DATETIME(3) | 更新时间 |

## 注意事项

- **仅覆盖固收+基金**（对应 tb_fd_category 中 c_type1_name LIKE '固收加%' 的基金）
- dev 环境此表未建立，查询会失败；生产环境正常

## 枚举值

### 风险特征标签（c_eq_risk_level）
| 取值 | 判断逻辑 |
|------|----------|
| 稳健 | 权益仓位均值 < 15% |
| 均衡 | 权益仓位均值 15%-25% |
| 激进 | 权益仓位均值 ≥ 25% |

### 股票转债策略标签（c_stk_cb_strategy）
| 取值 | 判断逻辑 |
|------|----------|
| 纯股票 | 转债仓位为0 |
| 股票为主转债为辅 | 转债/股票比值 < 1 |
| 股票转债均衡 | 转债/股票比值 1-4 |
| 转债为主股票为辅 | 转债/股票比值 > 4 |

### 择时标签（c_stk_timing / c_cb_timing）
| 字段 | 取值 | 判断逻辑 |
|------|------|----------|
| c_stk_timing | 择时/不择时 | 变动均值 ≥ 5% 为择时 |
| c_cb_timing | 择时/不择时 | 变动均值 ≥ 10% 为择时 |

## 常用查询示例

```sql
-- 查询激进型固收+基金（最新截面）
SELECT t.c_fd_code, b.c_short_name,
       t.c_eq_pos_avg, t.c_eq_risk_level, t.c_stk_cb_strategy
FROM tb_fd_tag_asset_fi t
JOIN tb_fd_basic_info b ON t.c_fd_code = b.c_fd_code
WHERE t.c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_tag_asset_fi)
  AND t.c_eq_risk_level = '激进'
ORDER BY t.c_eq_pos_avg DESC
LIMIT 20;
```
