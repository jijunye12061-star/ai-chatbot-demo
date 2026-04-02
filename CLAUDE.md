# CLAUDE.md

## 沟通语言

与用户交流时，默认使用**中文**回答。

## 开发文档体系

**每次开始工作前，先读这两个文件：**

| 文件                | 作用                           | 何时更新                            |
|-------------------|------------------------------|----------------------------------|
| `STATUS.md`       | 项目状态快照：当前阶段、最近完成、下一步、关键约束 | **每次完成开发任务后，覆盖更新（不是追加）**      |
| `ARCHITECTURE.md` | 代码地图，描述每个文件/目录的职责            | **新增、删除、重命名文件时同步更新**            |
| `CHANGELOG.md`    | 完整开发历史（仅供回溯，不必每次读）           | 重要里程碑完成后追加；日常任务可只更新 STATUS.md |
| 本文件 `CLAUDE.md`   | 项目总览和开发规范                    | 架构或规范变更时更新                      |

### 工作流程

1. 读 `STATUS.md`（~20 行）→ 了解当前状态和下一步计划
2. 读 `ARCHITECTURE.md` → 定位需要修改的文件，**不要盲目扫描整个代码库**
3. 完成开发后：
    - **覆盖更新** `STATUS.md`（保持 20-30 行，只记当前状态快照，不追加历史）
    - 如有重要里程碑，在 `CHANGELOG.md` 顶部追加条目
    - 如有文件增删，更新 `ARCHITECTURE.md`

## Project Overview

基金研究团队模型展示平台，当前处于 **Phase 1（AI 聊天 Demo）**。

- **Phase 1**：AI 问答机器人 Demo — 聊天界面 + SSE 流式输出（当前）
- **Phase 2**：模型展示页面 — Dashboard / 图表 / 数据下载
- **Phase 3**：AI 联动 — Function Calling 推荐模型页面

完整需求见 `docs/README.md`（文档导航索引）及 `docs/requirements/` 目录。

## Tech Stack

- **Frontend**: Vue 3 + Vite, Composition API (`<script setup>`), Markdown 渲染
- **Backend**: FastAPI (Python 3.11+), 类型注解, SSE 流式返回
- **Database**: 远程 SQL 服务（开发，经堡垒机反向代理访问 Doris） / Doris 直连（生产），详见 `docs/dev/remote-db.md`
- **LLM**: DeepSeek-V3（东财 API 代理），通过 `backend/config.py` 配置，`LLM_API_KEY` 环境变量注入
- **Communication**: SSE — `data: {"content": "...", "done": false}`

## Commands

```bash
# 后端
cd backend && uvicorn main:app --reload --port 8000

# 前端
cd frontend && npm run dev     # Dev server, /api 代理到 :8000
cd frontend && npm run build   # 生产构建

# 数据库（dev 环境无需本地数据库，通过远程 SQL 服务查询 Doris）
# 确保 backend/.env 中配置了 REMOTE_SQL_TOKEN
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
- `llm/client.py` 是唯一调用 LLM 的地方；`agents/orchestrator.py` 是 AI 请求总入口
- 多 Agent 分层：Router → Orchestrator → Agent → Tool，详见 `docs/requirements/03-ai-agent.md`
- 多轮对话上下文由前端以 `history` 传入，后端无状态
- 环境切换通过 `APP_ENV` 环境变量：dev（远程 SQL 服务） / prod（Doris 直连）
- 暂不实现：登录鉴权、对话持久化、token 截断、主题定制