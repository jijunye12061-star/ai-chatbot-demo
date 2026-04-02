# 开发数据库说明

## 架构概述

开发环境通过远程 SQL 查询服务访问 Doris 真实数据，无需本地数据库。

```
本机后端 (localhost:8000)
  → HTTP POST /sql
  → 公网反向代理 (https://tytapitest.1234567.com.cn/ty/sql)
  → 内网堡垒机（剥掉 /ty 前缀后转发）
  → SQL 查询服务 (10.189.26.145:9033)
  → Doris 数据库 (tytdata)
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

### 部署信息

| 项目 | 值 |
|------|-----|
| 内网机器 | 10.189.26.145 |
| 服务端口 | 9033 |
| 公网地址 | https://tytapitest.1234567.com.cn/ty |
| 代码目录 | 内网机器 `D:\jjy\sql_service\` |
| Python 环境 | conda env `sql_service` (Python 3.11) |
| 日志目录 | `D:\jjy\sql_service\logs\service.log` |

### 反向代理路径映射

反向代理**剥掉 `/ty` 前缀**后转发到内网服务：

| 公网请求路径 | 内网服务收到 |
|-------------|-------------|
| `/ty` | `/` |
| `/ty/sql` | `/sql` |
| `/ty/health` | `/health` |

### 接口

```
POST /sql
Header: Authorization: Bearer <token>
Body:   {"sql": "SELECT ...", "params": [...]}
→ Response: {"columns": [...], "rows": [...], "row_count": N}

GET /health
→ Response: {"status": "ok"}
```

支持绑定变量（pymysql `%s` 占位符）：

```json
{
  "sql": "SELECT * FROM tb_fd_basic_info WHERE c_fd_code = %s",
  "params": ["000001"]
}
```

### 安全机制

- **Token 认证**：请求头 `Authorization: Bearer <token>`，不匹配返回 403
- **IP 白名单**：`config.yaml` 中配置，支持 CIDR 网段（如 `10.189.0.0/16`），留空则不限制
- **只读校验**：只允许 SELECT 语句，拦截 INSERT/UPDATE/DELETE/DROP 等
- **行数限制**：默认最多返回 5000 行
- **查询超时**：Doris `query_timeout`，默认 10 秒
- **数据序列化**：Decimal → float、date/datetime → string、bytes → string

### 服务文件结构

```
D:\jjy\sql_service\
├── sql_service.py     # 服务主文件（FastAPI）
├── config.yaml        # 配置文件（Token、IP白名单、DB连接、限制参数）
├── start_service.bat  # 启动脚本（conda activate + python）
└── logs/
    └── service.log    # 运行日志（请求记录 + 错误堆栈）
```

### config.yaml 模板

```yaml
auth_token: "your-secret-token"

ip_whitelist:
  - "10.189.0.0/16"     # 内网网段

database:
  host: "doris-host-ip"
  port: 9030
  user: "readonly_user"
  password: "readonly_pass"
  database: "tytdata"

limits:
  max_rows: 5000
  query_timeout_seconds: 10
```

### 服务管理

```bash
# 进入内网机器后
conda activate sql_service
cd D:\jjy\sql_service

# 启动
python sql_service.py

# 查看日志
type logs\service.log            # Windows
# tail -f logs/service.log       # Linux

# 配置修改后需重启服务
```

### 持久化（Windows 任务计划）

```powershell
# 注册开机自启任务（管理员 PowerShell）
$action = New-ScheduledTaskAction -Execute "D:\jjy\sql_service\start_service.bat" -WorkingDirectory "D:\jjy\sql_service"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "SQLQueryService" -Action $action -Trigger $trigger -Settings $settings -User "SYSTEM" -RunLevel Highest

# 管理命令
Start-ScheduledTask -TaskName "SQLQueryService"     # 手动启动
Stop-ScheduledTask -TaskName "SQLQueryService"      # 手动停止
Get-ScheduledTask -TaskName "SQLQueryService"       # 查看状态
Unregister-ScheduledTask -TaskName "SQLQueryService" -Confirm:$false  # 删除任务
```

## 新增表操作清单

每次新增一张表时，按以下顺序同步更新：

```
□ docs/table_specs_source/tb_xxx/              新建 schema.sql + SPEC.md
□ backend/templates/table_catalog.md           加一行（极简目录）
□ backend/templates/table_specs/tb_xxx.md      新建详细字段说明
□ backend/tools/schema_reader.py               VALID_TABLES 加表名
□ backend/tests/test_sql_safety.py             test_allow_all_whitelist_tables 更新
```

> 无需本地导入数据 — 远程服务直接查询 Doris，表结构以 Doris 为准。

## 注意事项

- 远程服务需要内网机器保持运行，服务中断时开发环境无法查询数据
- 健康检查：`GET https://tytapitest.1234567.com.cn/ty/health` 返回 `{"status":"ok"}` 则服务正常
- Doris 库名为 `tytdata`，dev/prod 统一通过远程服务查同一个库
- 查询返回的数据类型由远程服务 JSON 序列化决定，Decimal → float、date → string
- PowerShell 终端显示中文可能乱码（编码问题），实际数据是正确的 UTF-8
