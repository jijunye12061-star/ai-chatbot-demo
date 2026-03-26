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

### `agents/base.py` — FC 循环

在每次工具调用前后 yield thinking 事件：

```python
# 调用工具前
yield thinking_event(step=f"正在执行：{tool_name}...", status="running")

# 调用工具后（成功）
yield thinking_event(step=f"{tool_name} 完成", status="done")

# 调用工具后（失败）
yield thinking_event(step=f"{tool_name} 失败，正在重试...", status="error")
```

### `tools/sql_executor.py` — 结果分流

SQL 执行后，工具层负责：

1. 截取前5条 + 总数，拼成 Markdown 表格文本 → 返回给 LLM 作为工具结果（进入上下文）
2. 将完整结果序列化为 `result_data` SSE 事件 → 直接 yield 给前端（绕过 LLM）

> 只有 `execute_sql` 工具触发 `result_data`；其他工具（schema_reader、screen_guide_reader 等）不触发。

### `api/chat.py` — StreamingResponse

透传所有 SSE 事件类型，不做过滤。

---

## 四、前端变更

### 新增组件

**`components/chat/ThinkingTimeline.vue`**

Props：
- `steps: Array<{step: string, status: 'done'|'running'|'error'}>`
- `collapsed: Boolean`

行为：
- `collapsed=false`：展示完整时间轴（阶段一）
- `collapsed=true`：展示胶囊摘要按钮，点击切换展开/折叠（阶段二/三）
- 答案开始输出（收到第一个 `type:content` 事件）时，自动折叠

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
