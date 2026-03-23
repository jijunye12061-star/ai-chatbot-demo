# API 契约

> 前后端接口规范。后端在 `backend/api/` 下实现，前端在 `frontend/src/api/` 下封装调用。

---

## POST /api/chat — AI 问答（SSE 流式）

**请求体**

```json
{
  "message": "用户输入的问题",
  "history": [
    { "role": "user",      "content": "上一轮用户问题" },
    { "role": "assistant", "content": "上一轮 AI 回答" }
  ]
}
```

- `message`：本轮用户输入（必填）
- `history`：历史对话列表（可为空数组），`role` 只允许 `user` / `assistant`

**响应**：`Content-Type: text/event-stream`，SSE 格式逐 chunk 推送

```
data: {"content": "部分文字", "done": false}
data: {"content": "更多文字", "done": false}
data: {"content": "",         "done": true}
```

- `done: false`：正在流式输出，`content` 追加到当前消息
- `done: true`：输出完毕，`content` 为空字符串

---

## GET /api/models — 模型元数据列表

**响应**

```json
[
  {
    "id": "yield-curve",
    "name": "收益率曲线",
    "status": "active",
    "route": "/models/yield-curve"
  }
]
```

---

## GET /api/models/{id}/data — 模型页面数据

**路径参数**：`id` — 模型 ID（如 `yield-curve`）

**响应**：各模型自定义 JSON 结构，由 `backend/services/model_data_service.py` 返回。

DB 不可用时降级返回空数据，前端显示 mock 数据。

---

## 错误处理约定

- LLM 调用异常：SSE 流中推送一条 `content: "请求出错：..."` 后结束
- SQL 安全校验失败：工具返回错误描述，由 LLM 转述给用户
- DB 连接失败：模型数据接口返回空数组，不影响聊天功能
