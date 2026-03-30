from typing import Protocol, Awaitable
from zoe_exceptions.http_exceptions.exc_domain import DomainException
from zoe_http.request import Request
from zoe_http.response import Response

class ErrorHandler(Protocol):
    def __call__(self, exception: DomainException, request: Request) -> Response | Awaitable[Response]:
        ...
