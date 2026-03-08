from typing import Any, Protocol, runtime_checkable
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_exceptions.exc_internal_exc import InternalServerException

@runtime_checkable
class Handler(Protocol):
    def handle(self, request: Request) -> Response:
        raise InternalServerException(
                detail=f"Handler '{type(self).__name__}' must implement the handle() method"
            )
