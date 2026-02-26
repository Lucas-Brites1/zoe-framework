from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode

from typing import Callable
from datetime import datetime
import time

class _Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREY    = "\033[90m"
    WHITE   = "\033[97m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"

_METHOD_COLORS = {
    "GET":     _Color.GREEN,
    "POST":    _Color.BLUE,
    "PUT":     _Color.YELLOW,
    "PATCH":   _Color.MAGENTA,
    "DELETE":  _Color.RED,
}

def _method_tag(method: str) -> str:
    color = _METHOD_COLORS.get(method, _Color.WHITE)
    return f"{color}{_Color.BOLD}{method:<7}{_Color.RESET}"

def _status_tag(status_code: HttpCode) -> str:
    code = status_code.value
    if isinstance(code, tuple):
        code = code[0]
    if code < 300:
        color = _Color.GREEN
    elif code < 400:
        color = _Color.CYAN
    elif code < 500:
        color = _Color.YELLOW
    else:
        color = _Color.RED
    return f"{color}{_Color.BOLD}{code}{_Color.RESET}"

def _duration_tag(ms: float) -> str:
    if ms < 100:
        color = _Color.GREEN
    elif ms < 500:
        color = _Color.YELLOW
    else:
        color = _Color.RED
    return f"{color}{ms:.1f}ms{_Color.RESET}"


class Logger(Middleware):
    def __init__(self, application_name: str | None = None, verbose: bool = False) -> None:
        self.__name = application_name
        self.__verbose = verbose

    def __call__(self, request: Request, next: Callable) -> Response:
        start = time.perf_counter()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        response: Response = next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000

        prefix = f"{_Color.BOLD}{_Color.CYAN}[{self.__name}]{_Color.RESET} " if self.__name else ""
        method  = _method_tag(request.method.value)
        status  = _status_tag(response.status_code)
        duration = _duration_tag(elapsed_ms)
        ts      = f"{_Color.GREY}{timestamp}{_Color.RESET}"
        route   = f"{_Color.WHITE}{request.route}{_Color.RESET}"

        print(f"{prefix}{ts}  {method}  {route}  {status}  {duration}")

        if self.__verbose:
            print(f"  {_Color.GREY}headers: {dict(request.headers)}{_Color.RESET}")
            if request.body:
                print(f"  {_Color.GREY}body:    {request.body}{_Color.RESET}")

        return response
