from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_http.bytes import Bytes

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
        """Middleware that logs every HTTP request processed by the server.
        ---

        **Args:**
            `application_name` *(str)*: Label shown at the start of every log line.
            `verbose` *(bool)*: If True, also logs request headers and body.
                **Default to False**

        **Example:**
        ```python
            app.use(Logger(application_name="MyApp"))

            app.use(Logger(application_name="MyApp", verbose=True))
        ```
        """
        self.__name = application_name
        self.__verbose = verbose
        self.__big_payload_warn: bool = True
        self.__big_payload_threshold: Bytes = Bytes.from_kb(n=10) # > 10KiB warning (1024 * 10 bytes)


    def set_big_payload_threshold(self, threshold: Bytes) -> "Logger":
        """
        Sets the maximum body size that will be logged in verbose mode.
    
        If the request body exceeds this threshold, the Logger will display
        a warning instead of printing the full body content.
        ---

        **Args:**
        - `threshold` *(Bytes)* — Maximum loggable body size.
        Use `Bytes.from_kb()` or `Bytes.from_mb()` to build the value.

        **Returns:**
        - `Logger` — returns self for method chaining.

        **Default:** `Bytes.from_kb(10)` *(10 KiB)*

        ---

        **Example:**
        ```python
            app.use(
                Logger("MyApp", verbose=True)
                    .set_big_payload_threshold(Bytes.from_kb(20))
            )
        ```
        """
        self.__big_payload_threshold = threshold.value
        return self

    
    def disable_big_payload_warning(self) -> "Logger":
        """
            Disables the big payload warning in verbose mode.
            ---
            By default, Logger warns when a request body exceeds the threshold
            instead of printing it - protecting the terminal from beign flooded 
            by large payloads. Call this method to turn off this protection.

            *Note:* not recommended for production environments.
        """
        self.__big_payload_warn = False
        return self

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
            if request.body:
                if request.content_length:
                    if request.content_length > self.__big_payload_threshold.value:
                        if self.__big_payload_warn:
                            print(f"{_Color.GREY}body: {_Color.RED}[payload too large to display — {_Color.BOLD}{request.content_length / 1024:.1f}KB]{_Color.RESET}")
                            print(f"    > {_Color.GREY}hint: {_Color.GREEN}call Logger().disable_big_payload_warning() to suppress this message")
                    else:
                        print(f"  {_Color.GREY}body:    {request.body}{_Color.RESET}")
                else:
                    print(f"{_Color.GREY}body: {_Color.YELLOW}[missing Content-Length header — skipping body log]{_Color.RESET}")

            print(f"  {_Color.GREY}headers: {dict(request.headers)}{_Color.RESET}")

        return response
