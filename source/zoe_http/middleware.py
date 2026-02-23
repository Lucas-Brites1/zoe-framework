from typing import Callable, Protocol
from zoe_http.request import Request
from zoe_http.response import Response

class Middleware(Protocol):
    def __call__(self, request: Request, next: Callable[[Request], Response]) -> Response:
        ...