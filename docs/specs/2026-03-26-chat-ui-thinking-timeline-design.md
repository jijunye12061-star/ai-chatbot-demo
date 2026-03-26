# 设计文档：AI 问答界面 · 思考时间轴 + 结构化结果展示

**日期**：2026-03-26
**状态**：已确认，待实施
**涉及范围**：前端聊天组件、后端 SSE 协议、Agent 工具层

---

## 背景与目标

当前 AI 问答界面（`/chat`）仅展示流式文本，用户无法感知 AI 正在执行什么操作（查询数据库、调用工具等），也无法获取结构化的筛选结果（如基金列表）用于进一步分析。

本次设计目标：
1. 在思考阶段实时展示工具调用进度（时间轴样式）
2. 筛选类结果以内嵌表格展示前5条，并提供完整结果的 Excel 下载
3. 整体 UI 风格对齐 Claude 网页版（无气泡助手回答、温暖米白背景）

---

## 一、UI 风格

### 整体基调（对齐 Claude 网页版）

| 元素 | 样式 |
|------|------|
| 页面背景 | `#f7f5f2`（温暖米白） |
| 侧边栏背景 | `#efede8`（保持现有风格） |
| 用户消息 | 浅米灰气泡 `#ebe9e3`，圆角18px |
| 助手消息 | **无气泡**，文字直接铺在背景上 |
| 字体 | Inter / system-ui，正文 15px，行高 1.8 |

### 三阶段状态

**阶段一：思考中**

助手回复区域显示展开的时间轴：

```
┌─────────────────────────────────┐
│ 思考过程                         │
│ ● 识别到基金筛选请求              │  ← 绿色实心点（完成）
│ ● 查询业绩数据，找到 847 只候选基金 │  ← 绿色实心点（完成）
│ ○ 正在过滤科技主题持仓占比...      │  ← 橙色空心点脉冲（进行中）
└─────────────────────────────────┘
```

**阶段二：流式输出中**

时间轴折叠为胶囊标签，正文开始出现：

```
[✓ 已完成 3 步 · 点击展开]

根据您的筛选条件，共找到 18 只符合要求的基金▌
```

**阶段三：完成**

胶囊标签保留（可点击展开步骤），正文 + 结果表格 + 下载按钮：

```
[✓ 已完成 3 步 · 点击展开]

根据您的筛选条件，共找到 18 只符合要求的基金，以下展示前 5 条：

┌────────────────────────────────────────────────┐
│ 前 5 条 / 共 18 条 · 按近1年收益排序             │
├──────────────┬──────┬──────┬────────┬──────────┤
│ 基金名称      │近1年 │近3年  │科技仓位 │规模(亿)  │
├──────────────┼──────┼──────┼────────┼──────────┤
│ 华夏科技创新  │+32.5%│+68.2%│  68%   │  45.3    │
│ ...          │      │      │        │          │
└──────────────┴──────┴──────┴────────┴──────────┘
│              还有 13 条                          │
└──────────────────────────────────────────────────┘

[📥 下载完整筛选结果.xlsx  18条]
```

---

## 二、SSE 协议扩展

### 新增事件类型

在现有协议基础上，新增 `type` 字段做事件分类。旧格式 `{"content": "...", "done": false}` 自动视为 `type: "content"`，向后兼容。

```jsonc
// 思考步骤（工具调用前后各发一次）
{"type": "thinking", "step": "识别到基金筛选请求", "status": "done"}
{"type": "thinking", "step": "正在查询业绩数据...", "status": "running"}
{"type": "thinking", "step": "数据获取失败，正在重试...", "status": "error"}

// 结构化数据旁路（完整结果，仅供前端 Excel 生成，不进 LLM 上下文）
{"type": "result_data", "columns": ["基金名称", "近1年", "近3年", "科技仓位", "规模"], "rows": [[...], ...]}

// 正文内容（原有）
{"type": "content", "content": "根据筛选条件...", "done": false}
{"type": "content", "content": "", "done": true}
```

### result_data 的旁路原则

- `result_data` 包含 SQL 查询的**完整行数**（可能上百条）
- LLM 上下文中**只注入摘要**（前5条 + 总数文本），不传入完整数据
- `result_data` 不写入多轮对话的 `history`，不污染后续对话

---

## 三、后端变更

### 完整数据流（后端）

```
sql_executor.py
  └─ 执行 SQL → 返回 ToolResult(summary_text, full_rows)
        ↓
agents/base.py（FC 循环）
  ├─ yield SSE: {"type":"thinking", ...}       ← 工具调用前后
  ├─ 将 summary_text 注入 tool 消息上下文       ← 进 LLM
  └─ 若 full_rows 存在: yield SSE: {"type":"result_data", ...}  ← 绕过 LLM
        ↓
agents/orchestrator.py
  └─ 将所有 yield 转为已格式化的 SSE 行（data: {...}\n\n）
        ↓
api/chat.py
  └─ StreamingResponse 透传，不再二次包装
```

### `tools/sql_executor.py` — 返回 ToolResult

`execute_sql` 从返回纯字符串改为返回结构化对象，由 `base.py` 统一处理分流：

```python
@dataclass
class ToolResult:
    summary: str          # 前5条 + 总数的 Markdown 表格文本，进入 LLM 上下文
    full_rows: list | None  # 完整行数据；若行数 <= 5 则为 None（不触发 result_data）
    columns: list | None    # 列名列表

# execute_sql 返回示例：
# ToolResult(
#   summary="查询结果：共 87 条，前5条如下：\n| 基金名称 | ...",
#   full_rows=[[...], ...],   # 所有 87 条
#   columns=["基金名称", "近1年", ...]
# )
```

> 只有 `execute_sql` 返回 `ToolResult`；其他工具仍返回纯字符串，`base.py` 做类型判断。
> 只有 `full_rows` 不为 None（即结果行数 > 5）时才 yield `result_data`，避免中间查询的单行结果弹出表格。

### `agents/base.py` — FC 循环

```python
# 1. 调用工具前 yield thinking（running）
yield format_sse({"type": "thinking", "step": f"正在查询：{tool_name}...", "status": "running"})

# 2. 执行工具
result = await execute_tool(tool_name, tool_args)

# 3. 调用工具后 yield thinking（done / error）
yield format_sse({"type": "thinking", "step": f"{friendly_name} 完成", "status": "done"})

# 4. 若是 ToolResult，分流处理
if isinstance(result, ToolResult):
    tool_message_content = result.summary          # 进 LLM 上下文
    if result.full_rows is not None:
        yield format_sse({                         # 绕过 LLM，直达前端
            "type": "result_data",
            "columns": result.columns,
            "rows": result.full_rows
        })
else:
    tool_message_content = result                  # 其他工具，纯字符串直接进上下文
```

### `agents/orchestrator.py` — SSE 格式化层

orchestrator 统一负责将所有 yield 内容格式化为完整 SSE 行，`api/chat.py` 只做透传：

```python
def format_sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
```

最终文本片段（`stream_text()` 输出）也封装为 `{"type": "content", "content": "...", "done": false}`，统一格式。

### `api/chat.py` — StreamingResponse

移除当前的二次包装逻辑（`{"content": chunk, "done": False}`），改为直接透传 orchestrator yield 出的已格式化 SSE 行：

```python
async def event_stream():
    async for line in orchestrator.run(message, history):
        yield line  # 已是完整的 "data: {...}\n\n" 格式
```

---

## 四、前端变更

### 完整数据流（前端）

```
api/chat.js（sendMessage）
  └─ 读取 SSE，解析 JSON，按 type 分发到回调
        ↓
stores/chat.js（send）
  ├─ onThinking(step, status) → 追加到 msg.thinkingSteps
  ├─ onResultData(columns, rows) → 赋值到 msg.resultData
  ├─ onChunk(content) → 追加到 msg.content；第一次时设 thinkingCollapsed=true
  └─ onDone() → 设 msg.streaming=false，写入 history
        ↓
MessageBubble.vue
  ├─ <ThinkingTimeline :steps="msg.thinkingSteps" v-model:collapsed="msg.thinkingCollapsed" />
  ├─ 渲染 msg.content（Markdown）
  └─ <ResultTable v-if="msg.resultData" :columns="..." :rows="..." />
```

### 新增组件

**`components/chat/ThinkingTimeline.vue`**

Props：
- `steps: Array<{step: string, status: 'done'|'running'|'error'}>`
- `collapsed: Boolean`（v-model 绑定，由父组件/Store 持有状态）

Emits：
- `update:collapsed`（Boolean）— 用户点击展开/折叠时通知父组件

行为：
- `collapsed=false`：展示完整时间轴卡片（阶段一）
- `collapsed=true`：展示胶囊摘要按钮，点击时 emit `update:collapsed` → Store 更新 `thinkingCollapsed`
- 折叠状态由 Store 的 `thinkingCollapsed` 字段持有，组件是纯受控组件，不自管状态

**`components/chat/ResultTable.vue`**

Props：
- `columns: string[]`
- `rows: any[][]`
- `previewCount: number`（默认 5）

行为：
- 展示前 `previewCount` 条，底部显示剩余数量提示
- "下载 Excel" 按钮：使用 SheetJS（xlsx.js）在浏览器内生成 `.xlsx` 并触发下载
- 若 `rows.length <= previewCount`，不显示下载按钮和剩余提示

### 修改组件

**`components/chat/MessageBubble.vue`**

- 助手消息：去掉气泡背景/边框/阴影，文字直接渲染
- 气泡上方插入 `<ThinkingTimeline>`（仅 role=assistant 且有 steps 时）
- 文字内容中支持渲染 `<ResultTable>`（收到 result_data 后插入）

**`ChatWindow.vue`**

- 背景色改为 `#f7f5f2`

### 修改 `api/chat.js` — SSE 解析

`sendMessage()` 增加 `onThinking` 和 `onResultData` 回调参数，SSE 解析按 `type` 分发：

```js
// 新签名
sendMessage(text, history, { onChunk, onThinking, onResultData, onDone, onError })

// SSE 解析逻辑
const event = JSON.parse(data)
if (!event.type || event.type === 'content') {
  if (event.done) onDone()
  else onChunk(event.content)
} else if (event.type === 'thinking') {
  onThinking(event.step, event.status)
} else if (event.type === 'result_data') {
  onResultData(event.columns, event.rows)
}
```

旧的 `onChunk` / `onDone` / `onError` 单参数调用方式保持向后兼容（检测第三个参数类型）。

### 修改 Store（`stores/chat.js`）

消息对象新增字段：

```js
{
  role: 'assistant',
  content: '',
  streaming: true,
  thinkingSteps: [],      // 新增：思考步骤数组
  thinkingCollapsed: false, // 新增：时间轴是否折叠
  resultData: null,        // 新增：{ columns, rows } 或 null
}
```

SSE 解析按 type 分流：

```js
if (event.type === 'thinking')    → 追加到 msg.thinkingSteps
if (event.type === 'result_data') → 赋值到 msg.resultData
if (event.type === 'content')     → 追加到 msg.content；若是第一个 content 事件，设 thinkingCollapsed=true
if (!event.type)                  → 兼容旧格式，视为 content
```

---

## 五、依赖

| 依赖 | 用途 | 引入方式 |
|------|------|----------|
| SheetJS（xlsx） | 浏览器内生成 .xlsx | `npm install xlsx` |

---

## 六、不在本次范围内

- 思考步骤的文案国际化
- 结果表格的列排序/筛选交互
- Excel 文件的样式美化（列宽、颜色等）
- 非 `execute_sql` 工具的结构化结果展示
