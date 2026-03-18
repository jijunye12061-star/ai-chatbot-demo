# 本地开发数据库说明

## 环境概述

本地开发使用 Docker MySQL 8.0 模拟生产环境的 Doris 数据库。Doris 兼容 MySQL 协议和大部分 SQL 语法，因此本地查询语句可直接复用到生产环境。

本地开发只关心**查询入口是否合理**，即查询能跑通、字段名对得上即可。

## 容器信息

| 项目  | 值             |
|-----|---------------|
| 容器名 | dev-mysql     |
| 镜像  | mysql:8.0     |
| 端口  | 3306          |
| 用户名 | root          |
| 密码  | dev           |
| 数据库 | fund_platform |

### 启动命令

```bash
docker run -d --name dev-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=dev -e MYSQL_DATABASE=fund_platform mysql:8.0
```

### 日常操作

```bash
# 启动（容器停了的情况）
docker start dev-mysql

# 停止
docker stop dev-mysql

# 进入 MySQL 命令行
docker exec -it dev-mysql mysql -uroot -pdev fund_platform
```

## 数据库表结构

共 9 张表，全部基于生产 Doris 的表/视图结构转换而来。视图在本地统一转为普通表，字段名保持一致。

| 表名                     | 说明           | 主键                                        | 预估行数     |
|------------------------|--------------|---------------------------------------------|----------|
| tb_fd_basic_info       | 基金基础信息       | c_fd_code                                   | ~500     |
| tb_fd_category         | 基金组内分类（自研）   | c_report_date, c_fd_code                    | ~1,200   |
| tb_fd_nav_daily        | 每日净值         | c_trade_date, c_fd_code                     | ~144,000 |
| tb_fd_asset_allocation | 资产配置（季报）     | c_fd_code, c_report_date, c_style           | ~1,600   |
| tb_fd_portfolio_bd     | 债券持仓明细（季报）   | c_fd_code, c_report_date, c_bd_code, c_style | ~21,000  |
| tb_fd_portfolio_stk    | 股票持仓明细（季报）   | c_fd_code, c_report_date, c_stk_code, c_style | ~22,000 |
| tb_fd_perform_abs      | 绝对收益指标（按区间）  | c_fd_code, c_trade_date, c_period_code      | ~82,000  |
| tb_dict_params         | 通用参数字典（行业分类） | c_param_type, c_param_code                  | ~3,100   |
| tb_fd_tag_asset_eq     | 权益基金资产配置标签   | c_fd_code, c_report_date                    | ~330     |

### 建表脚本

文件：`data/schema_mysql.sql`

执行方式：

```bash
docker cp data/schema_mysql.sql dev-mysql:/tmp/
docker exec -i dev-mysql mysql -uroot -pdev < data/schema_mysql.sql
```

## 测试数据

数据从 Doris 通过 Python + pandas 导出为 CSV，再通过 `LOAD DATA` 导入本地 MySQL。

### 导出（在能访问 Doris 的机器上）

```python
import pandas as pd
import pymysql

conn = pymysql.connect(host='doris_host', port=9030, user='xxx', password='xxx', database='tytdata')

tables = {
    'tb_fd_basic_info': "SELECT * FROM tb_fd_basic_info",
    'tb_fd_nav_daily': "SELECT * FROM tb_fd_nav_daily WHERE c_trade_date >= '2024-01-01'",
    # ... 其他表
}

for name, sql in tables.items():
    df = pd.read_sql(sql, conn)
    df.to_csv(f'data/{name}.csv', index=False)
```

### 导入本地

```bash
# 复制 CSV 进容器
docker cp data/tb_fd_basic_info.csv dev-mysql:/tmp/
docker cp data/tb_fd_nav_daily.csv dev-mysql:/tmp/

# 进入 MySQL 开启 local_infile
docker exec -it dev-mysql mysql -uroot -pdev --local-infile=1 fund_platform

# 在 MySQL 内执行
SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE '/tmp/tb_fd_basic_info.csv'
INTO TABLE tb_fd_basic_info
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### 当前数据量

| 表名 | 行数 |
|------|------|
| tb_fd_basic_info | ~500 |
| tb_fd_category | ~1,200 |
| tb_fd_nav_daily | ~144,000 |
| tb_fd_asset_allocation | ~1,600 |
| tb_fd_portfolio_stk | ~22,000 |
| tb_fd_portfolio_bd | ~21,000 |
| tb_fd_perform_abs | ~82,000 |
| tb_dict_params | ~3,100 |
| tb_fd_tag_asset_eq | ~330 |

> 导入时的 warnings 为空字符串与 NULL 的转换问题，不影响查询测试。

## 后端配置切换

`backend/config.py` 通过环境变量区分 dev / prod：

```python
import os

ENV = os.getenv("APP_ENV", "dev")

DB_CONFIG = {
    "dev": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "dev",
        "database": "fund_platform",
    },
    "prod": {
        "host": "<doris_host>",
        "port": 9030,
        "user": "<prod_user>",
        "password": "<prod_password>",
        "database": "tytdata",
    },
}[ENV]
```

本地开发默认 `dev`，生产部署时设 `APP_ENV=prod`。

## 注意事项

- Doris 视图在本地是普通表，需要手动维护数据同步（定期重新导出导入）
- Doris 特有语法（`DISTRIBUTED BY`、`PROPERTIES` 等）已在建表脚本中移除
- 生产环境的 schema 是 `tytdata`，本地统一用 `fund_platform`，后端 config 处理这个差异
- CSV 导入的空值会变成空字符串而非 NULL，查询时注意用 `WHERE col != ''` 而非 `WHERE col IS NOT NULL`