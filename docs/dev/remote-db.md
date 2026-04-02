# 开发数据库说明

## 架构概述

开发环境通过远程 SQL 查询服务访问 Doris 真实数据，无需本地数据库。

```
本机后端 (localhost:8000)
  → HTTP POST /sql
  → 公网反向代理 (https://tytapitest.1234567.com.cn/ty/sql)
  → 内网堡垒机
  → SQL 查询服务 (10.189.26.145:9033)
  → Doris 数据库
```

## 后端配置

`backend/.env` 中需要配置：

```env
# APP_ENV 默认 dev，自动走远程 SQL 服务
REMOTE_SQL_TOKEN=<your-token>
```

`config.py` 环境切换：

| APP_ENV | 数据库模式 | 说明 |
|---------|----------|------|
| dev（默认）| remote | 通过 HTTP 调用远程 SQL 服务查询 Doris |
| prod | direct | pymysql 直连 Doris |

## 远程 SQL 服务

部署在内网机器 `10.189.26.145:9033`，代码位于该机器的 `~/sql_service/` 目录。

### 接口

```
POST /sql
Header: Authorization: Bearer <token>
Body:   {"sql": "SELECT ...", "params": [...]}
→ Response: {"columns": [...], "rows": [...], "row_count": N}
```

### 安全机制

- Token 认证（Bearer）
- IP 白名单（可选，在 `config.yaml` 中配置）
- 只允许 SELECT 语句
- 危险关键词拦截（INSERT/UPDATE/DELETE/DROP 等）
- 返回行数限制（默认 5000）
- 查询超时控制（默认 10s）

### 服务管理

```bash
# SSH 到内网机器后
conda activate sql_service
cd ~/sql_service

# 启动
python sql_service.py

# 后台运行
nohup python sql_service.py > service.log 2>&1 &

# 查看日志
tail -f service.log

# 配置修改（Token、IP白名单、数据库连接等）
vim config.yaml
# 改完需重启服务
```

## 新增表操作清单

每次新增一张表时，按以下顺序同步更新：

```
□ docs/table_specs_source/tb_xxx/       新建 schema.sql + insert.py + SPEC.md
□ backend/templates/table_catalog.md    加一行（极简目录）
□ backend/templates/table_specs/tb_xxx.md   新建详细字段说明
□ backend/tools/schema_reader.py        VALID_TABLES 加表名
□ backend/tests/test_sql_safety.py      test_allow_all_whitelist_tables 更新
```

> 无需本地导入数据 — 远程服务直接查询 Doris，表结构以 Doris 为准。

## 注意事项

- 远程服务需要内网机器保持运行，服务中断时开发环境无法查询数据
- Doris 库名为 `tytdata`，与之前本地 `fund_platform` 不同，但后端 config 已处理
- 查询返回的数据类型由远程服务 JSON 序列化决定，Decimal 等类型会转为 float/string
