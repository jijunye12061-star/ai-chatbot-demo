# CLAUDE.md

## 沟通语言

与用户交流时，默认使用**中文**回答。

## 开发文档体系

**每次开始工作前，先读这三个文件：**

| 文件                | 作用                 | 何时更新                   |
|-------------------|--------------------|------------------------|
| `CHANGELOG.md`    | 开发日志，按时间倒序记录每次做了什么 | **每次完成开发任务后，在顶部追加新条目** |
| `ARCHITECTURE.md` | 代码地图，描述每个文件/目录的职责  | **新增、删除、重命名文件时同步更新**   |
| 本文件 `CLAUDE.md`   | 项目总览和开发规范          | 架构或规范变更时更新             |

### 工作流程

1. 读 `CHANGELOG.md` 最新条目 → 了解当前进度和下一步计划
2. 读 `ARCHITECTURE.md` → 定位需要修改的文件，**不要盲目扫描整个代码库**
3. 完成开发后：
    - 更新 `CHANGELOG.md` 顶部（完成了什么、进行中、下一步）
    - 如有文件增删，更新 `ARCHITECTURE.md`

## Project Overview

基金研究团队模型展示平台，当前处于 **Phase 1（AI 聊天 Demo）**。

- **Phase 1**：AI 问答机器人 Demo — 聊天界面 + SSE 流式输出（当前）
- **Phase 2**：模型展示页面 — Dashboard / 图表 / 数据下载
- **Phase 3**：AI 联动 — Function Calling 推荐模型页面

完整需求见 `docs/基金研究团队模型展示平台需求文档.md` 和 `docs/AI问答机器人Demo需求文档.md`。

## Tech Stack

- **Frontend**: Vue 3 + Vite, Composition API (`<script setup>`), Markdown 渲染
- **Backend**: FastAPI (Python 3.11+), 类型注解, SSE 流式返回
- **Database**: Docker MySQL 8.0（本地开发） / Doris（生产），详见 `docs/LOCAL_DEV_DB.md`
- **LLM**: 可切换（OpenAI / Claude / 本地模型），通过 `backend/config.py` 配置
- **Communication**: SSE — `data: {"content": "...", "done": false}`

## Commands

```bash
# 后端
cd backend && uvicorn main:app --reload --port 8000

# 前端
cd frontend && npm run dev     # Dev server, /api 代理到 :8000
cd frontend && npm run build   # 生产构建

# 数据库
docker start dev-mysql
```

## API Contract

`POST /api/chat` — SSE streaming response

```json
// Request
{
  "message": "用户问题",
  "history": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ]
}

// SSE chunks
data: {"content": "部分文字", "done": false}
data: {"content": "", "done": true}
```

## Key Architecture Notes

- Vite dev server 代理 `/api` → `http://localhost:8000`，配置在 `vite.config.js`
- `llm_service.py` 是唯一调用 LLM 的地方，`api/chat.py` 只负责转发流
- LLM 供应商可通过 `config.py` 切换，service 层抽象差异
- 多轮对话上下文由前端以 `history` 传入，后端无状态
- 环境切换通过 `APP_ENV` 环境变量（dev / prod）
- 暂不实现：登录鉴权、对话持久化、token 截断、主题定制