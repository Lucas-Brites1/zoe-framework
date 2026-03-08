from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_non_http_aggregate import ZoeNonHttpAggregate
from zoe_http.code import HttpCode
from zoe_http.request import Request
import sys
import traceback
from datetime import datetime


class _C:
    RED    = "\033[38;5;203m"
    ORANGE = "\033[38;5;215m"
    YELLOW = "\033[38;5;221m"
    CYAN   = "\033[38;5;116m"
    GRAY   = "\033[38;5;245m"
    WHITE  = "\033[97m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

    TL = "╭"; TR = "╮"; BL = "╰"; BR = "╯"
    H  = "─"; V  = "│"
    ML = "├"; MR = "┤"


class _Printer:
    MIN_WIDTH = 50
    MAX_WIDTH = 100
    PADDING   = 6  # "│" + "  " left + "  " right + "│"

    @classmethod
    def _calc_width(cls, label: str, *blocks: str) -> int:
        candidates = [len(label) + 4]  # title padding
        for block in blocks:
            for line in block.splitlines():
                candidates.append(len(line) + cls.PADDING)
        return max(cls.MIN_WIDTH, min(cls.MAX_WIDTH, max(candidates)))

    @classmethod
    def _box_top(cls, label: str, color: str, width: int) -> None:
        title = f" {label} "
        pad   = width - 2 - len(title)
        print(
            f"{color}{_C.TL}{_C.H * (pad // 2)}{title}{_C.H * (pad - pad // 2)}{_C.TR}{_C.RESET}",
            file=sys.stderr
        )

    @classmethod
    def _box_bottom(cls, color: str, width: int) -> None:
        print(f"{color}{_C.BL}{_C.H * (width - 2)}{_C.BR}{_C.RESET}\n", file=sys.stderr)

    @classmethod
    def _divider(cls, color: str, width: int) -> None:
        print(f"{color}{_C.ML}{_C.H * (width - 2)}{_C.MR}{_C.RESET}", file=sys.stderr)

    @classmethod
    def _blank(cls, color: str) -> None:
        print(f"{color}{_C.V}{_C.RESET}", file=sys.stderr)

    @classmethod
    def _row(cls, key: str, value: str, key_color: str, val_color: str, border_color: str) -> None:
        lines = str(value).splitlines() or [""]
        for i, line in enumerate(lines):
            prefix = f"{key_color}{key:<14}{_C.RESET}" if i == 0 else " " * 14
            print(f"{border_color}{_C.V}{_C.RESET}  {prefix}{val_color}{line}{_C.RESET}", file=sys.stderr)

    @classmethod
    def _text_block(cls, text: str, color: str, border_color: str) -> None:
        for line in text.splitlines():
            print(f"{border_color}{_C.V}{_C.RESET}  {color}{line}{_C.RESET}", file=sys.stderr)

    @classmethod
    def _section(cls, label: str, content: str, label_color: str, content_color: str, border_color: str) -> None:
        print(f"{border_color}{_C.V}{_C.RESET}  {label_color}{_C.BOLD}{label}{_C.RESET}", file=sys.stderr)
        cls._blank(border_color)
        cls._text_block(content, content_color, border_color)

    @classmethod
    def internal_error(cls, error: ZoeNonHttpError, request: Request | None) -> None:
        color     = _C.RED
        label     = "ZOE — INTERNAL ERROR"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(error, ZoeNonHttpAggregate):
            all_blocks = [e.explain + "\n" + e.fix for e in error.errors]
        else:
            all_blocks = [error.explain, error.fix]

        width = cls._calc_width(label, error.why, *all_blocks)

        cls._box_top(label, color, width)
        cls._blank(color)
        cls._row("timestamp", timestamp, _C.GRAY, _C.WHITE,  color)
        cls._row("error",     error.why, _C.GRAY, _C.ORANGE, color)

        if request:
            cls._blank(color)
            cls._divider(color, width)
            cls._blank(color)
            cls._row("method", request.method.value, _C.GRAY, _C.YELLOW, color)
            cls._row("route",  request.route,        _C.GRAY, _C.WHITE,  color)
            cls._row("client", request.client_ip,    _C.GRAY, _C.WHITE,  color)

        if isinstance(error, ZoeNonHttpAggregate):
            for i, e in enumerate(error.errors, 1):
                cls._blank(color)
                cls._divider(color, width)
                cls._blank(color)
                cls._section(f"Problem {i}", e.explain, _C.GRAY, _C.WHITE, color)
                cls._blank(color)
                cls._section(f"Fix {i}",     e.fix,     _C.CYAN, _C.WHITE, color)
        else:
            cls._blank(color)
            cls._divider(color, width)
            cls._blank(color)
            cls._section("Problem", error.explain, _C.GRAY, _C.WHITE, color)
            cls._blank(color)
            cls._divider(color, width)
            cls._blank(color)
            cls._section("Fix",     error.fix,     _C.CYAN, _C.WHITE, color)

        cls._blank(color)
        cls._box_bottom(color, width)

    @classmethod
    def unexpected_error(cls, error: Exception, request: Request | None) -> None:
        color     = _C.ORANGE
        label     = "ZOE — UNEXPECTED EXCEPTION"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb        = traceback.format_exc()

        width = cls._calc_width(label, str(error), tb)

        cls._box_top(label, color, width)
        cls._blank(color)
        cls._row("timestamp", timestamp,            _C.GRAY, _C.WHITE,  color)
        cls._row("type",      type(error).__name__, _C.GRAY, _C.ORANGE, color)
        cls._row("message",   str(error),           _C.GRAY, _C.WHITE,  color)

        if request:
            cls._blank(color)
            cls._divider(color, width)
            cls._blank(color)
            cls._row("method", request.method.value, _C.GRAY, _C.YELLOW, color)
            cls._row("route",  request.route,        _C.GRAY, _C.WHITE,  color)
            cls._row("client", request.client_ip,    _C.GRAY, _C.WHITE,  color)

        cls._blank(color)
        cls._divider(color, width)
        cls._blank(color)
        cls._text_block(tb, _C.DIM + _C.WHITE, color)
        cls._blank(color)
        cls._box_bottom(color, width)


class InternalServerException(ZoeHttpException):
    def __init__(self, detail: str = "An unexpected error occurred.") -> None:
        super().__init__(message=detail, status_code=HttpCode.INTERNAL_SERVER_ERROR)

    @classmethod
    def from_non_http_error(
        cls,
        error: ZoeNonHttpError,
        request: Request | None = None,
        show_in_terminal: bool = True,
    ) -> "InternalServerException":
        if show_in_terminal:
            _Printer.internal_error(error, request)
        return cls(detail="Internal server error. Check server logs for details.")

    @classmethod
    def from_unexpected_error(
        cls,
        error: Exception,
        request: Request | None = None,
        show_in_terminal: bool = True,
    ) -> "InternalServerException":
        if show_in_terminal:
            _Printer.unexpected_error(error, request)
        return cls(detail="Unexpected error occurred. Check server logs.")
