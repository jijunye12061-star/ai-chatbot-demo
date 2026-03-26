import json
from enum import Enum
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from agents.orchestrator import run as agent_run
from utils.conv_logger import ConversationLogger, set_conv_logger

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

    logger = ConversationLogger(request.message, history_count=len(request.history))
    set_conv_logger(logger)

    async def event_stream():
        response_buf = []
        try:
            async for sse_line in agent_run(request.message, history):
                yield sse_line  # 已是完整的 "data: {...}\n\n" 格式，直接透传
                # 解析 SSE 事件写入日志
                if sse_line.startswith("data: "):
                    try:
                        payload = json.loads(sse_line[6:])
                        t = payload.get("type")
                        if t == "thinking":
                            logger.thinking(payload.get("step", ""), payload.get("status", ""))
                        elif t == "content":
                            chunk = payload.get("content", "")
                            if chunk:
                                response_buf.append(chunk)
                            if payload.get("done") and response_buf:
                                logger.response("".join(response_buf))
                                response_buf.clear()
                        elif t == "result_data":
                            row_count = len(payload.get("rows") or [])
                            logger._write(f"[{logger._ts()}] [DATA] 返回 {row_count} 行结果数据")
                    except Exception:
                        pass
        except Exception as e:
            print(f"[API] 异常: {type(e).__name__}: {e}")
            logger.error(f"{type(e).__name__}: {e}")
            err_line = f"data: {json.dumps({'type': 'content', 'content': f'请求出错：{str(e)}', 'done': False}, ensure_ascii=False)}\n\n"
            yield err_line
            yield f"data: {json.dumps({'type': 'content', 'content': '', 'done': True})}\n\n"
        finally:
            logger.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
