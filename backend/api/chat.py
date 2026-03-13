from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from services.llm_service import stream_chat

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []


@router.post("/chat")
def chat(request: ChatRequest):
    print(f"[API] 收到请求: message='{request.message[:50]}', history 条数={len(request.history)}")
    return StreamingResponse(
        stream_chat(request.message, request.history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
