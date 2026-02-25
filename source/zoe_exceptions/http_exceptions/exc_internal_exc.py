from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.code import HttpCode

class InternalServerException(ZoeHttpException):
    def __init__(self: "InternalServerException", detail: str = "An unexpected error occurred.") -> None:
        super().__init__(
            message=detail,
            status_code=HttpCode.INTERNAL_SERVER_ERROR
        )