from typing import Callable, Protocol, runtime_checkable

from zoe_http.request import Request
from zoe_http.response import Response

@runtime_checkable
class Middleware(Protocol):
    def process(self, request: Request, next: Callable[[Request], Response]) -> Response:
        raise NotImplementedError("Middleware protocol must implement process() function")

