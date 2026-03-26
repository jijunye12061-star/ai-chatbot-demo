"""
对话日志：每次请求生成独立日志文件，记录工具调用链和 LLM 回复，用于 debug。
日志目录：backend/logs/（已加入 .gitignore）

使用方式：
  - api/chat.py 在每个请求开始时调用 set_conv_logger()
  - 其他模块调用 get_conv_logger() 获取当前请求的 logger
  - contextvars 保证不同并发请求互不干扰
"""
import os
from contextvars import ContextVar
from datetime import datetime
from typing import Optional

_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
_current: ContextVar[Optional["ConversationLogger"]] = ContextVar("conv_logger", default=None)


class ConversationLogger:
    def __init__(self, message: str, history_count: int = 0):
        os.makedirs(_LOG_DIR, exist_ok=True)
        self._start = datetime.now()
        ts = self._start.strftime("%Y%m%d_%H%M%S")
        safe = "".join(c if c.isalnum() else "_" for c in message[:24]).strip("_")
        self.path = os.path.join(_LOG_DIR, f"{ts}_{safe}.log")
        self._f = open(self.path, "w", encoding="utf-8")
        self._write("=" * 60)
        self._write(f"问题: {message}")
        self._write(f"历史消息: {history_count} 条")
        self._write("=" * 60)
        self._write("")

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def _write(self, text: str):
        self._f.write(text + "\n")
        self._f.flush()

    def tool_call(self, name: str, args: str):
        self._write(f"[{self._ts()}] >> TOOL: {name}")
        self._write(f"               ARGS: {args[:600]}")

    def tool_result(self, name: str, summary: str):
        brief = summary[:300].replace("\n", " ")
        self._write(f"[{self._ts()}] << RESULT: {name}  -> {brief}")
        self._write("")

    def thinking(self, step: str, status: str):
        icon = {"running": "...", "done": "OK", "error": "ERR"}.get(status, "   ")
        self._write(f"[{self._ts()}] [{icon}] {step}")

    def response(self, text: str):
        self._write(f"[{self._ts()}] -- LLM 回复 --")
        self._write(text)
        self._write("")

    def error(self, msg: str):
        self._write(f"[{self._ts()}] [ERROR] {msg}")

    def close(self):
        elapsed = (datetime.now() - self._start).total_seconds()
        self._write("=" * 60)
        self._write(f"对话结束，耗时 {elapsed:.2f}s")
        self._f.close()


def set_conv_logger(logger: ConversationLogger):
    _current.set(logger)


def get_conv_logger() -> Optional[ConversationLogger]:
    return _current.get()
