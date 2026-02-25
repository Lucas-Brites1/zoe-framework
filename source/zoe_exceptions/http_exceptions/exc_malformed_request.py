from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.code import HttpCode

class MalformedRequestException(ZoeHttpException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            message=f"Malformed request: {detail}",
            status_code=HttpCode.BAD_REQUEST
        )