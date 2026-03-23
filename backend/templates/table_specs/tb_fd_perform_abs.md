# tb_fd_perform_abs — 基金绝对收益指标表

**主键**: (c_fd_code, c_trade_date, c_period_code) | **更新频率**: 日度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_trade_date | DATE | 计算截止交易日期 |
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_period_code | VARCHAR(10) | 计算区间代码（见枚举，**重要**） |
| c_period_ret | DECIMAL(10,4) | 区间收益率（**已是%，25.5=25.5%**） |
| c_ann_ret | DECIMAL(10,4) | 年化收益率（**已是%**） |
| c_ann_vol | DECIMAL(10,4) | 年化波动率（**已是%**，正数） |
| c_up_side_vol | DECIMAL(18,4) | 上行波动率（**已是%**，正数） |
| c_down_side_vol | DECIMAL(10,4) | 下行波动率（**已是%**，正数） |
| c_mdd | DECIMAL(10,4) | 最大回撤（**已是%，正数**，25.5=回撤25.5%） |
| c_sharpe | DECIMAL(15,4) | 夏普比率（纯数值，无单位） |
| c_calmar | DECIMAL(15,4) | 卡尔玛比率（年化收益/最大回撤，无单位） |
| c_sortino | DECIMAL(15,4) | 索提诺比率（纯数值，无单位） |
| c_skewness | DECIMAL(10,4) | 偏度（正值=右偏，负值=左偏） |
| c_kurtosis | DECIMAL(10,4) | 峰度（>3尖峰，<3平坦） |
| c_break_ratio | DECIMAL(18,4) | 盈利天数比例（%，大于0的净值增长日占比） |
| c_updatetime | DATETIME(3) | 更新时间 |

## 注意事项

- **收益率、波动率、回撤均已是百分比形式（已×100），不需要再乘以100**
  - c_period_ret = 25.5 表示区间收益率 25.5%
  - c_mdd = 15.3 表示最大回撤 15.3%（正数）
- 夏普/卡尔玛/索提诺是纯比率，无单位
- 数据不足时（如成立不满1年查1年指标）字段为 NULL 或空字符串
- 本地数据 c_trade_date 在 2025-12-01 ~ 2025-12-31 之间
- 查询最新指标：ORDER BY c_trade_date DESC LIMIT N
- c_up_side_vol 和 c_down_side_vol 分别衡量上行/下行波动，均为正数、已是 %
- c_break_ratio = 60.0 表示 60% 的交易日净值为正增长

## 枚举值

### 计算区间代码（c_period_code）— 必须记住这个枚举
| 代码 | 含义 |
|------|------|
| 00 | 近1月 |
| 01 | 近3月 |
| 02 | 近6月 |
| 03 | 近1年 |
| 04 | 近2年 |
| 05 | 近3年 |
| 06 | 近5年 |
| 07 | 今年以来（年初至今/YTD） |
| 08 | 成立以来 |

## 常用查询示例

```sql
-- 查询某基金近1年的夏普比率和最大回撤
SELECT c_fd_code, c_trade_date,
       c_period_ret, c_ann_ret, c_ann_vol,
       c_mdd, c_sharpe, c_calmar, c_sortino
FROM tb_fd_perform_abs
WHERE c_fd_code = '000001'
  AND c_period_code = '03'
ORDER BY c_trade_date DESC
LIMIT 1;

-- 查询某基金所有区间的风险指标（最新截面）
SELECT c_period_code,
       c_period_ret, c_ann_ret, c_ann_vol, c_mdd,
       c_sharpe, c_calmar
FROM tb_fd_perform_abs
WHERE c_fd_code = '000001'
  AND c_trade_date = '2025-12-31'
ORDER BY c_period_code
LIMIT 10;

-- 筛选近1年夏普比率优秀的基金
SELECT p.c_fd_code, b.c_short_name,
       p.c_ann_ret, p.c_ann_vol, p.c_mdd, p.c_sharpe
FROM tb_fd_perform_abs p
JOIN tb_fd_basic_info b ON p.c_fd_code = b.c_fd_code
WHERE p.c_period_code = '03'
  AND p.c_trade_date = '2025-12-31'
  AND p.c_sharpe > 1.5
  AND p.c_mdd < 20
ORDER BY p.c_sharpe DESC
LIMIT 20;
```
