# 后端架构审查报告

> 审查范围：`backend/` 目录，聚焦四个 AI 问答场景（闲聊、数据查询、基金筛选、报告生成）
> 目标读者：Claude Code，按优先级逐项修复

---

## 整体评价

项目架构清晰，多 Agent 分层（Router → Orchestrator → Agent → Tool）设计合理，Function Calling 循环、SQL 安全校验、模板化筛选等核心机制都已跑通。以下问题按 **P0（必须修）→ P1（建议修）→ P2（后续改进）** 排列。

---

## P0 — 安全 / 必须立即修复

### 1. API Key 硬编码在 `config.py` 中

**文件**：`backend/config.py`

**现状**：
```python
API_KEY = "VOplCUjdbDBjO1Zf4f2eE5CcBd244835Ad31D5F6Ab7699F9"
```
API Key 直接写在代码里，如果代码推送到任何远程仓库（哪怕是内部 Git），都有泄露风险。

**修复方案**：
```python
API_KEY = os.getenv("LLM_API_KEY", "")
if not API_KEY:
    raise ValueError("环境变量 LLM_API_KEY 未设置")
```
在项目根目录提供 `.env.example` 模板（不含真实值），`.env` 加入 `.gitignore`。本地开发时用 `.env` 文件或在启动命令中传入环境变量。

### 2. `BaseAgent.run()` — FC 循环达到上限时静默结束

**文件**：`backend/agents/base.py`

**现状**：`max_iterations = 10` 的 for 循环如果跑满，不会 yield 任何内容，用户看到空回复。

**修复方案**：在循环后添加兜底：
```python
for _ in range(max_iterations):
    # ... 现有逻辑 ...
else:
    # 循环跑满未 break — yield 一条兜底消息
    yield "抱歉，处理过程过于复杂，请尝试简化问题。"
    print(f"[{self.name}] ⚠️ FC 循环达到上限 {max_iterations}")
```

---

## P1 — 健壮性 / 建议尽快修复

### 3. LLM 调用无超时和重试

**文件**：`backend/llm/client.py`

**现状**：`AsyncOpenAI` 初始化和调用没有设置 `timeout`。如果 LLM 服务不稳定（东财代理偶尔慢），请求会一直挂着，SSE 连接不断开。

**修复方案**：
```python
from openai import AsyncOpenAI
import httpx

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=httpx.Timeout(connect=10, read=120, write=10, pool=10),
    max_retries=2,  # openai SDK 内置重试（仅对 5xx / 网络错误）
)
```
`read=120` 给报告生成等长时间任务留足空间；`max_retries=2` 利用 SDK 自带的指数退避。

### 4. 数据库连接没有连接池

**文件**：`backend/db/connection.py`

**现状**：每次 `execute_query()` 都 `pymysql.connect()` → 查询 → `conn.close()`。在并发场景下频繁建连效率低，且有连接耗尽风险。

**修复方案**：用 `DBUtils.PooledDB` 包一层（轻量级，不需要换 ORM）：
```python
from dbutils.pooled_db import PooledDB

_pools = {}

def _get_pool(readonly: bool = False) -> PooledDB:
    key = "ro" if readonly else "rw"
    if key not in _pools:
        cfg = _RO_CONFIG if readonly else DB_CONFIG
        _pools[key] = PooledDB(
            creator=pymysql,
            maxconnections=10,
            host=cfg["host"], port=cfg["port"],
            user=cfg["user"], password=cfg["password"],
            database=cfg["database"], charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    return _pools[key]

def get_connection(readonly: bool = False):
    return _get_pool(readonly).connection()
```
安装：`pip install DBUtils`。`execute_query()` 不需要改，因为 `conn.close()` 在 PooledDB 下是归还连接而非断开。

### 5. Orchestrator 路由失败无降级处理

**文件**：`backend/agents/orchestrator.py`

**现状**：如果 `_router.classify()` 抛异常（网络超时、LLM 返回畸形等），整个请求直接炸掉。

**修复方案**：
```python
try:
    intent = await _router.classify(messages)
except Exception as e:
    print(f"[Orchestrator] 路由失败: {e}，降级到 chat")
    intent = "chat"
```

### 6. `BaseAgent` — 无工具 Agent 浪费一次非流式调用

**文件**：`backend/agents/base.py`

**现状**：`ChatAgent`（`tool_names=[]`）走 `run()` 时，会先做一次非流式 `chat_completion()`，发现没有 tool_calls，才做流式输出。相当于每次闲聊都调用了两次 LLM。

**修复方案**：在 `run()` 开头加快速路径：
```python
async def run(self, messages: list) -> AsyncGenerator[str, None]:
    full_messages = [{"role": "system", "content": self.system_prompt}] + list(messages)

    # 快速路径：无工具的 Agent 直接流式输出
    if not self.tool_names:
        async for chunk in stream_text(full_messages):
            yield chunk
        return

    # 有工具 → 进入 FC 循环
    tool_schemas = get_tool_schemas(self.tool_names)
    # ... 现有循环逻辑 ...
```
这样 ChatAgent 只需一次 LLM 调用，延迟和成本都直接减半。

### 7. `_execute_tool` 使用已废弃的 `get_event_loop()`

**文件**：`backend/agents/base.py`

**现状**：
```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, lambda: func(**args))
```
Python 3.10+ 中 `get_event_loop()` 在没有 running loop 的场景下会报 DeprecationWarning。

**修复方案**：
```python
result = await asyncio.to_thread(func, **args)
```
`asyncio.to_thread()` 是 Python 3.9+ 的推荐替代，更简洁且行为一致。

### 8. 重复的 JSON 序列化器

**文件**：`backend/tools/fund_filter.py` 和 `backend/tools/sql_executor.py`

**现状**：两个文件各自定义了 `default_serializer` / `_default_serializer`，逻辑完全一样（处理 Decimal 和 datetime）。

**修复方案**：提取到公共位置，比如 `backend/utils/serializers.py`：
```python
import decimal
import datetime

def json_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    return str(obj)
```
两个文件改为 `from utils.serializers import json_default`。

---

## P2 — 代码质量 / 后续改进

### 9. `llm/client.py` 有未使用的 import

```python
import json  # 未使用，可删除
```

### 10. `RouterAgent.__init__` 在模块加载时读文件

**文件**：`backend/agents/router_agent.py`

**现状**：`RouterAgent.__init__` 读取 `router.md` 并替换 `{today}`。但 `_router = RouterAgent()` 是在 `orchestrator.py` 模块级实例化的，这意味着 `today` 在进程启动时就固定了。如果后端长时间运行不重启，`today` 会变成"昨天"甚至更早。

**修复方案**：将 `today` 注入推迟到 `classify()` 调用时：
```python
class RouterAgent:
    def __init__(self):
        prompt_path = os.path.join(_PROMPTS_DIR, "router.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self._template = f.read()  # 只存模板

    async def classify(self, messages: list) -> str:
        today = date.today().strftime("%Y-%m-%d")
        system_prompt = self._template.replace("{today}", today)
        # ... 后续不变 ...
```
同理，`FundScreenerAgent._load_prompt` 中的 `today` 也应考虑相同处理。

### 11. `ChatRequest.history` 缺少 `role` 枚举校验

**文件**：`backend/api/chat.py`

**现状**：
```python
class Message(BaseModel):
    role: str  # 任意字符串
    content: str
```
如果前端传入 `role: "system"` 或乱填值，会直接拼入 LLM messages。

**修复方案**：
```python
from enum import Enum

class Role(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(BaseModel):
    role: Role
    content: str
```

### 12. `CORS allow_origins` 需要生产环境适配

**文件**：`backend/main.py`

**现状**：
```python
allow_origins=["http://localhost:5173"]
```
部署到生产后需要加上实际域名。建议改为根据 `ENV` 环境变量动态设置：
```python
CORS_ORIGINS = {
    "dev": ["http://localhost:5173"],
    "prod": [os.getenv("FRONTEND_ORIGIN", "https://your-domain.com")],
}
```

### 13. `db/safety.py` 表白名单与 `ALLOWED_TABLES` 硬编码耦合

**现状**：新增表时需要同时改 `safety.py`、`test_sql_safety.py`、`table_catalog.md`、`table_specs/` 四个地方。

**改进方向**：考虑从 `table_specs/` 目录自动生成白名单（读文件名），减少一个手动同步点：
```python
import glob
_SPECS_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "table_specs")
ALLOWED_TABLES = {
    os.path.splitext(os.path.basename(f))[0]
    for f in glob.glob(os.path.join(_SPECS_DIR, "*.md"))
}
```
前提是 table_specs 下的文件名与表名一致。

### 14. 缺少结构化日志

**现状**：全部用 `print()` 输出日志，无级别、无时间戳、无请求 ID。在生产环境中不利于排查问题。

**改进方向**：引入 Python `logging` 模块：
```python
import logging
logger = logging.getLogger("fund_platform")
```
可以后续再加 JSON 格式化和请求 ID 追踪，但先至少把 `print()` 替换为 `logger.info/warning/error`。

### 15. 测试覆盖不足

**现状**：只有 `test_sql_safety.py`（14 cases）和 `test_screen_template.py`（12 cases），都是纯逻辑单测。

**建议后续补充**：
- `test_router_agent.py`：mock LLM，验证各种意图的路由正确性和关键词兜底
- `test_base_agent.py`：mock LLM 和 tool，验证 FC 循环边界（多轮工具调用、工具报错、达到上限）
- `test_chat_api.py`：FastAPI TestClient 验证 SSE 格式正确性

---

## 修复执行顺序建议

对于当前阶段「把问答机器人主要场景做出来」的目标，建议按以下顺序处理：

1. **P0 #1**（API Key）— 安全问题，5 分钟搞定
2. **P1 #6**（无工具 Agent 快速路径）— 直接减半 ChatAgent 延迟，体验提升明显
3. **P1 #3**（LLM 超时重试）— 防止请求挂死
4. **P0 #2**（FC 循环兜底）— 防止用户看到空回复
5. **P1 #5**（路由降级）— 防止路由失败导致整个请求挂掉
6. **P1 #7**（废弃 API 替换）— 一行代码
7. **P1 #8**（重复序列化器）— 小重构
8. **P2 项**按需处理

---

*生成时间：2026-03-23*
