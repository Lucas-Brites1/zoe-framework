from typing import Protocol, Coroutine, Any, runtime_checkable, Callable, Awaitable

from zoe_http.request import Request
from zoe_http.response import Response

@runtime_checkable
class Middleware(Protocol):
    def process(self, request: Request, next: Callable[[Request], Awaitable[Response]]) -> Response | Awaitable[Response]:
        raise NotImplementedError("Middleware protocol must implement process() function")

