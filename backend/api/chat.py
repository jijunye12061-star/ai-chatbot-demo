import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from agents.orchestrator import run as agent_run

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []


@router.post("/chat")
async def chat(request: ChatRequest):
    print(f"[API] 收到请求: message='{request.message[:50]}', history 条数={len(request.history)}")

    # 将 Pydantic 模型转为 dict
    history = [{"role": m.role, "content": m.content} for m in request.history]

    async def event_stream():
        try:
            async for chunk in agent_run(request.message, history):
                yield f"data: {json.dumps({'content': chunk, 'done': False}, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[API] 异常: {type(e).__name__}: {e}")
            yield f"data: {json.dumps({'content': f'请求出错：{str(e)}', 'done': False}, ensure_ascii=False)}\n\n"
        finally:
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
