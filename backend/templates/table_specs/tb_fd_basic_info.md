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
| c_terminate_reason | VARCHAR(100) | 终止原因 |
| c_manager_code | VARCHAR(200) | 基金经理代码（多人逗号分隔） |
| c_custodian_code | VARCHAR(50) | 托管银行代码 |
| c_invest_standard | TEXT | 投资标准（资产配置比例约定） |
| c_transform_date | DATE | 转型生效日期 |
| c_regular_open_status | VARCHAR(10) | 定开情况（1=是/0=否） |
| c_min_hold_period | DECIMAL(18,2) | 最短持有期（单位：月） |
| c_sales_fee_rate | VARCHAR(20) | 销售服务费率 |
| c_init_code | VARCHAR(20) | 初始代码 |
| c_updatetime | DATETIME(3) | 更新时间 |

## 注意事项

- CSV 导入后空值存为空字符串，判断终止（已清盘）用 `c_terminate_date != ''`，非空表示已清盘
- c_class1_code IN ('001','002','003','004') 是主要基金类型（股票/混合/债券/货币）
- c_regular_open_status = '1' 表示定期开放基金，'0' 表示非定开
- c_min_hold_period 非空表示持有期基金（单位：月）
- 筛选普通开放式基金：`c_regular_open_status = '0' AND c_min_hold_period IS NULL`

## 枚举值

### 基金分类层级（c_class1/2/3_code）

| 一级分类 | 二级分类 | 三级分类 |
|----------|----------|----------|
| 001 股票型基金 | 001001 普通股票型基金 | 001001001 普通股票型基金 |
|  | 001002 指数型股票基金 | 001002001 被动指数型基金 |
|  |  | 001002002 增强指数型基金 |
| 002 混合型基金 | 002001 偏股混合型基金 | 002001001 偏股混合型基金 |
|  | 002002 平衡混合型基金 | 002002001 平衡混合型基金 |
|  | 002003 偏债混合型基金 | 002003001 偏债混合型基金 |
|  | 002004 灵活配置型基金 | 002004001 灵活配置型基金 |
|  | 002005 其他混合型基金 | 002005001 其他混合型基金 |
| 003 债券型基金 | 003001 纯债型基金 | 003001001 中长期纯债型基金 |
|  |  | 003001002 短期纯债型基金 |
|  | 003002 混合债券型基金 | 003002001 混合债券型一级基金 |
|  |  | 003002002 混合债券型二级基金 |
|  | 003003 指数型债券基金 | 003003001 被动指数型债券基金 |
|  |  | 003003002 增强指数型债券基金 |
| 004 货币型基金 | 004001 传统货币型基金 | 004001001 传统货币型基金 |
|  | 004002 浮动净值型货币基金 | 004002001 浮动净值型货币基金 |
| 005 QDII基金 | 005001 QDII股票型基金 | 005001001 QDII普通股票型基金 |
|  |  | 005001002 QDII被动指数型基金 |
|  |  | 005001003 QDII增强指数型基金 |
|  | 005002 QDII混合型基金 | 005002001 QDII偏股混合型基金 |
|  |  | 005002002 QDII平衡混合型基金 |
|  |  | 005002003 QDII偏债混合型基金 |
|  |  | 005002004 QDII灵活配置型基金 |
|  | 005003 QDII债券型基金 | 005003001 QDII混合债券型基金 |
|  | 005004 QDII-FOF | 005004001 QDII-FOF |
|  | 005005 QDII-另类投资基金 | 005005001 QDII商品型基金 |
|  |  | 005005002 QDII-REITs |
| 006 FOF | 006001 股票型FOF | 006001001 股票型FOF |
|  | 006002 混合型FOF | 006002001 偏股混合型FOF |
|  |  | 006002002 平衡混合型FOF |
|  |  | 006002003 偏债混合型FOF |
|  | 006003 债券型FOF | 006003001 债券型FOF |
|  | 006006 养老目标FOF | 006006001 养老目标日期FOF |
|  |  | 006006002 养老目标风险FOF |
| 007 另类投资基金 | 007001 基础设施REITs | 007001001 基础设施REITs |
|  | 007002 商品型基金 | 007002001 商品型基金 |
|  | 007003 量化对冲基金 | 007003001 量化对冲基金 |

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
