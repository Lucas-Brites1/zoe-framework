from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.code import HttpCode

class NotFoundException(ZoeHttpException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            status_code=HttpCode.NOT_FOUND,
            message=f"{resource} not found."
        )
