import os
import re
import sys
import textwrap
import traceback
from datetime import datetime

from zoe_exceptions.exc_non_http_aggregate import ZoeNonHttpAggregate
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.code import HttpCode
from zoe_http.request import Request

_ANSI = re.compile(r'\033\[[0-9;]*m')


def _visible(text: str) -> int:
    """Return the visible (non-ANSI) length of a string."""
    return len(_ANSI.sub('', text))


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
    MIN_WIDTH  = 50
    MAX_WIDTH  = 150
    # Every content row is: │ + "  " + content + padding + "  " + │  = 6 overhead chars
    PADDING    = 6
    # Key column width used in _row
    KEY_WIDTH  = 14

    @classmethod
    def _terminal_width(cls) -> int:
        try:
            return os.get_terminal_size().columns
        except OSError:
            return cls.MAX_WIDTH

    @classmethod
    def _calc_width(cls, label: str, *blocks: str) -> int:
        candidates = [len(label) + 4]
        for block in blocks:
            for line in block.splitlines():
                candidates.append(len(line) + cls.PADDING)
        return max(cls.MIN_WIDTH, min(cls._terminal_width(), max(candidates)))

    # Each of the _print_* helpers below satisfies:
    #   1 (│) + 2 (spaces) + <visible content> + <pad> + 2 (spaces) + 1 (│) == width

    @classmethod
    def _pad_for(cls, visible_content_len: int, width: int) -> int:
        """Right-side padding so the closing │ lands exactly at `width`."""
        return max(0, width - cls.PADDING - visible_content_len)

    @classmethod
    def _box_top(cls, label: str, color: str, width: int) -> None:
        title  = f" {label} "
        total  = width - 2 - len(title)          # dashes on both sides
        left   = total // 2
        right  = total - left
        print(
            f"{color}{_C.TL}{_C.H * left}{title}{_C.H * right}{_C.TR}{_C.RESET}",
            file=sys.stderr,
        )

    @classmethod
    def _box_bottom(cls, color: str, width: int) -> None:
        print(f"{color}{_C.BL}{_C.H * (width - 2)}{_C.BR}{_C.RESET}\n", file=sys.stderr)

    @classmethod
    def _divider(cls, color: str, width: int) -> None:
        print(f"{color}{_C.ML}{_C.H * (width - 2)}{_C.MR}{_C.RESET}", file=sys.stderr)

    @classmethod
    def _blank(cls, color: str, width: int) -> None:
        print(f"{color}{_C.V}{' ' * (width - 2)}{_C.V}{_C.RESET}", file=sys.stderr)

    @classmethod
    def _print_line(cls, content: str, color: str, width: int) -> None:
        """Print a single bordered line with arbitrary (possibly ANSI-coloured) content."""
        pad = cls._pad_for(_visible(content), width)
        print(
            f"{color}{_C.V}{_C.RESET}  {content}{' ' * pad}  {color}{_C.V}{_C.RESET}",
            file=sys.stderr,
        )

    @classmethod
    def _row(cls, key: str, value: str, key_color: str, val_color: str, border_color: str, width: int) -> None:
        """Print a key-value row, wrapping long values across multiple lines."""
        max_val_width = width - cls.PADDING - cls.KEY_WIDTH
        lines = str(value).splitlines() or [""]

        for i, line in enumerate(lines):
            for j, wline in enumerate(textwrap.wrap(line, width=max_val_width) or [""]):
                if i == 0 and j == 0:
                    key_raw     = f"{key_color}{key:<{cls.KEY_WIDTH}}{_C.RESET}"
                    key_visible = cls.KEY_WIDTH           # key is always plain ASCII
                else:
                    key_raw     = " " * cls.KEY_WIDTH
                    key_visible = cls.KEY_WIDTH

                content_raw     = f"{key_raw}{val_color}{wline}{_C.RESET}"
                visible_content = key_visible + len(wline)
                pad = cls._pad_for(visible_content, width)

                print(
                    f"{border_color}{_C.V}{_C.RESET}  {content_raw}{' ' * pad}  {border_color}{_C.V}{_C.RESET}",
                    file=sys.stderr,
                )

    @classmethod
    def _text_block(cls, text: str, color: str, border_color: str, width: int) -> None:
        """Print a block of plain text, wrapping to fit inside the box."""
        max_content = width - cls.PADDING
        for line in text.splitlines():
            for wline in textwrap.wrap(line, width=max_content) or [""]:
                pad = cls._pad_for(len(wline), width)
                print(
                    f"{border_color}{_C.V}{_C.RESET}  {color}{wline}{_C.RESET}{' ' * pad}  {border_color}{_C.V}{_C.RESET}",
                    file=sys.stderr,
                )

    @classmethod
    def _section(cls, label: str, content: str, label_color: str, content_color: str, border_color: str, width: int) -> None:
        """Print a labelled section header followed by a text block."""
        pad = cls._pad_for(len(label), width)
        print(
            f"{border_color}{_C.V}{_C.RESET}  {label_color}{_C.BOLD}{label}{_C.RESET}{' ' * pad}  {border_color}{_C.V}{_C.RESET}",
            file=sys.stderr,
        )
        cls._blank(border_color, width)
        cls._text_block(content, content_color, border_color, width)

    @classmethod
    def internal_error(cls, error: ZoeNonHttpError, request: Request | None) -> None:
        color     = _C.RED
        label     = "ZOE — INTERNAL ERROR"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(error, ZoeNonHttpAggregate):
            extra_blocks = [e.explain + "\n" + e.fix for e in error.errors]
        else:
            extra_blocks = [error.explain, error.fix]

        width = cls._calc_width(label, error.why, *extra_blocks)

        cls._box_top(label, color, width)
        cls._blank(color, width)
        cls._row("timestamp", timestamp, _C.GRAY, _C.WHITE,  color, width)
        cls._row("error",     error.why, _C.GRAY, _C.ORANGE, color, width)

        if request:
            cls._blank(color, width)
            cls._divider(color, width)
            cls._blank(color, width)
            cls._row("method", request.method.value, _C.GRAY, _C.YELLOW, color, width)
            cls._row("route",  request.route,        _C.GRAY, _C.WHITE,  color, width)
            cls._row("client", request.client_ip,    _C.GRAY, _C.WHITE,  color, width)

        if isinstance(error, ZoeNonHttpAggregate):
            for i, e in enumerate(error.errors, 1):
                cls._blank(color, width)
                cls._divider(color, width)
                cls._blank(color, width)
                cls._section(f"Problem {i}", e.explain, _C.GRAY, _C.WHITE, color, width)
                cls._blank(color, width)
                cls._section(f"Fix {i}",     e.fix,     _C.CYAN, _C.WHITE, color, width)
        else:
            cls._blank(color, width)
            cls._divider(color, width)
            cls._blank(color, width)
            cls._section("Problem", error.explain, _C.GRAY, _C.WHITE, color, width)
            cls._blank(color, width)
            cls._divider(color, width)
            cls._blank(color, width)
            cls._section("Fix",     error.fix,     _C.CYAN, _C.WHITE, color, width)

        cls._blank(color, width)
        cls._box_bottom(color, width)

    @classmethod
    def unexpected_error(cls, error: Exception, request: Request | None) -> None:
        color     = _C.ORANGE
        label     = "ZOE — UNEXPECTED EXCEPTION"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb        = traceback.format_exc()

        width = cls._calc_width(label, str(error), tb)

        cls._box_top(label, color, width)
        cls._blank(color, width)
        cls._row("timestamp", timestamp,            _C.GRAY, _C.WHITE,  color, width)
        cls._row("type",      type(error).__name__, _C.GRAY, _C.ORANGE, color, width)
        cls._row("message",   str(error),           _C.GRAY, _C.WHITE,  color, width)

        if request:
            cls._blank(color, width)
            cls._divider(color, width)
            cls._blank(color, width)
            cls._row("method", request.method.value, _C.GRAY, _C.YELLOW, color, width)
            cls._row("route",  request.route,        _C.GRAY, _C.WHITE,  color, width)
            cls._row("client", request.client_ip,    _C.GRAY, _C.WHITE,  color, width)

        cls._blank(color, width)
        cls._divider(color, width)
        cls._blank(color, width)
        cls._text_block(tb, _C.DIM + _C.WHITE, color, width)
        cls._blank(color, width)
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
