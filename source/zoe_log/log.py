from datetime import datetime

from zoe_log.context import _local
from zoe_log.loglevel import LogLevel, reset_color


class Log:
    @staticmethod
    def _context() -> str:
        full_ctx: str = ""
        context: str = getattr(_local, "context", "app")
        subcontext: str | None = getattr(_local, "subcontext", None)
        if subcontext:
            full_ctx = f"{context}.{subcontext}"
        else:
            full_ctx = context
        return full_ctx

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _header(level: LogLevel) -> str:
        return f"{level.color}{level.label:<10}{reset_color} [{Log._context()}] | {Log._now()}"

    @staticmethod
    def _final_message(level: LogLevel, message: str) -> str:
        return Log._header(level=level) + f" | {message}"

    @staticmethod
    def info(message: str) -> None:
        return print(Log._final_message(level=LogLevel.INFO, message=message))

    @staticmethod
    def debug(message: str) -> None:
        return print(Log._final_message(level=LogLevel.DEBUG, message=message))

    @staticmethod
    def warning(message: str) -> None:
        return print(Log._final_message(level=LogLevel.WARNING, message=message))

    @staticmethod
    def error(message: str) -> None:
        return print(Log._final_message(level=LogLevel.ERROR, message=message))

    @staticmethod
    def critical(message: str) -> None:
        return print(Log._final_message(level=LogLevel.CRITICAL, message=message))

    @staticmethod
    def stacktrace(message: str) -> None:
        import traceback

        print(Log._final_message(level=LogLevel.STACKTRACE, message=message))
        traceback.print_exc()
