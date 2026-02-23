from typing import Protocol, Any
from zoe_http.request import Request
from zoe_http.response import Response

class Handler:
    def __call__(self: "Handler", request: Request, **kwargs: Any) -> Response:
        raise NotImplementedError("Handler must implement __call__")