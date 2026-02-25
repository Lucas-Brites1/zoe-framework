from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.code import HttpCode

class MethodNotAllowedException(ZoeHttpException):
    def __init__(self, route: str, method: str) -> None:
        super().__init__(
            message=f"Method '{method}' is not allowed for '{route}'.",
            status_code=HttpCode.METHOD_NOT_ALLOWED
        )