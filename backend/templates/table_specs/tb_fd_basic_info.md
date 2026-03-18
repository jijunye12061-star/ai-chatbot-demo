# tb_fd_basic_info — 基金基础信息表

**主键**: c_fd_code | **更新频率**: 日度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_short_name | VARCHAR(100) | 基金简称 |
| c_full_name | VARCHAR(200) | 基金全称 |
| c_estabdate | DATE | 成立日期 |
| c_terminate_date | DATE | 终止日期（清盘日，在库为空字符串，非NULL） |
| c_class1_code | VARCHAR(10) | 一级分类代码（三位，见枚举） |
| c_class1_name | VARCHAR(50) | 一级分类名称 |
| c_class2_code | VARCHAR(10) | 二级分类代码（六位） |
| c_class2_name | VARCHAR(50) | 二级分类名称 |
| c_class3_code | VARCHAR(10) | 三级分类代码（九位） |
| c_class3_name | VARCHAR(50) | 三级分类名称 |
| c_manager_name | VARCHAR(100) | 基金经理名称（多人逗号分隔） |
| c_custodian_name | VARCHAR(100) | 托管银行名称 |
| c_company_code | VARCHAR(50) | 基金公司代码 |
| c_company_name | VARCHAR(100) | 基金公司简称 |
| c_invest_scope | TEXT | 投资范围说明 |
| c_purchase_status | VARCHAR(20) | 申购状态（见枚举） |
| c_redeem_status | VARCHAR(20) | 赎回状态（见枚举） |
| c_fund_nature | VARCHAR(50) | 基金性质（见枚举） |
| c_mgmt_fee_rate | VARCHAR(20) | 管理费率（字符串，如"1.20%"） |
| c_custodian_fee_rate | VARCHAR(20) | 托管费率（字符串） |

## 注意事项

- CSV 导入后空值存为空字符串，判断终止（已清盘）用 `c_terminate_date != ''`，非空表示已清盘
- c_class1_code IN ('001','002','003','004') 是主要基金类型（股票/混合/债券/货币）

## 枚举值

### 一级分类（c_class1_code）
| 代码 | 名称 |
|------|------|
| 001 | 股票型基金 |
| 002 | 混合型基金 |
| 003 | 债券型基金 |
| 004 | 货币型基金 |
| 005 | QDII基金 |
| 006 | FOF |
| 007 | 另类投资基金 |

### 申购状态（c_purchase_status）
开放申购 / 暂停申购 / 认购期 / 场内交易 / 封闭期 / 暂停交易 / 限大额

### 赎回状态（c_redeem_status）
开放赎回 / 暂停赎回 / 认购期 / 场内交易 / 封闭期 / 暂停交易

### 基金性质（c_fund_nature）
证券投资基金 / FOF / 联接基金 / MOM / 集合计划 / ETF / LOF / REITs

## 常用查询示例

```sql
-- 查询某基金基本信息
SELECT c_fd_code, c_short_name, c_class1_name, c_class3_name,
       c_manager_name, c_company_name, c_estabdate
FROM tb_fd_basic_info
WHERE c_fd_code = '000001'
LIMIT 1;

-- 查询某公司旗下股票型基金
SELECT c_fd_code, c_short_name, c_class3_name, c_manager_name, c_estabdate
FROM tb_fd_basic_info
WHERE c_company_name LIKE '%华夏%'
  AND c_class1_code = '001'
  AND c_terminate_date = ''
LIMIT 20;

-- 查询可申购的基金列表
SELECT c_fd_code, c_short_name, c_class1_name, c_company_name
FROM tb_fd_basic_info
WHERE c_purchase_status = '开放申购'
  AND c_terminate_date = ''
  AND c_class1_code IN ('001','002')
LIMIT 50;
```
