from typing import Any, Protocol
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException

class Handler(Protocol):
    def handle(self, request: Request) -> Response:
        raise InternalServerException(
                detail=f"Handler '{type(self).__name__}' must implement the handle() method"
            )
