# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 沟通语言

与用户交流时，默认使用**中文**回答。

## Project Overview

This is an AI chatbot demo using **Vue 3 + Vite** (frontend) and **FastAPI** (backend). The core feature is streaming AI responses via SSE (Server-Sent Events) with a typewriter effect. See `docs/AI问答机器人Demo需求文档.md` for full requirements.

## Tech Stack

- **Frontend**: Vue 3 + Vite, renders Markdown in AI responses
- **Backend**: FastAPI (Python), wraps LLM API and streams responses
- **Communication**: SSE — backend streams chunks as `data: {"content": "...", "done": false}`
- **LLM**: Configurable (OpenAI / Claude / local model) via `backend/config.py`

## Expected Project Structure

```
project/
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── components/
│   │   │   ├── ChatWindow.vue
│   │   │   ├── MessageBubble.vue
│   │   │   └── ChatInput.vue
│   │   └── api/chat.js        # Wraps POST /api/chat with SSE handling
│   ├── vite.config.js         # Proxies /api → localhost:8000
│   └── package.json
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── api/chat.py            # POST /api/chat route
│   ├── services/llm_service.py
│   └── config.py              # API keys, model params
└── requirements.txt
```

## Commands

### Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev     # Dev server with /api proxy to :8000
npm run build   # Production build
```

## API Contract

`POST /api/chat` — SSE streaming response

Request body:
```json
{
  "message": "user question",
  "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
}
```

SSE response chunks:
```
data: {"content": "partial text", "done": false}
data: {"content": "", "done": true}
```

## Key Architecture Notes

- The frontend Vite dev server proxies `/api` requests to `http://localhost:8000` — configure in `vite.config.js`
- `llm_service.py` is the single place where the LLM is called; the route in `api/chat.py` just streams its output forward
- LLM provider is swappable via `config.py` — the service layer should abstract provider differences
- Multi-turn context is passed from the frontend as `history`; no server-side session state
- Features explicitly out of scope: auth, persistence, token truncation, theming
