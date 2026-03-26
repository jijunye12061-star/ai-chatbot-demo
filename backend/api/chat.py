import json
from enum import Enum
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from agents.orchestrator import run as agent_run

router = APIRouter()


class Role(str, Enum):
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []


@router.post("/chat")
async def chat(request: ChatRequest):
    print(f"[API] 收到请求: message='{request.message[:50]}', history 条数={len(request.history)}")
    history = [{"role": m.role, "content": m.content} for m in request.history]

    async def event_stream():
        try:
            async for sse_line in agent_run(request.message, history):
                yield sse_line  # 已是完整的 "data: {...}\n\n" 格式，直接透传
        except Exception as e:
            print(f"[API] 异常: {type(e).__name__}: {e}")
            err_line = f"data: {json.dumps({'type': 'content', 'content': f'请求出错：{str(e)}', 'done': False}, ensure_ascii=False)}\n\n"
            yield err_line
            yield f"data: {json.dumps({'type': 'content', 'content': '', 'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
