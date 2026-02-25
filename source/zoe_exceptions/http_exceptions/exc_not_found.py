from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.request import Request
from zoe_http.code import HttpCode

class RouteNotFoundException(ZoeHttpException):
    def __init__(self: "RouteNotFoundException", request: Request) -> None:
        super().__init__(
            message=f"Route '{request.route}' not found for method {request.method.name}",
            status_code=HttpCode.NOT_FOUND
        )