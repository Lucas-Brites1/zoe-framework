from zoe_http.response import Response
from zoe_http.code import HttpCode

class ZoeHttpException(Exception):
    def __init__(self, message: str, status_code: HttpCode = HttpCode.INTERNAL_SERVER_ERROR) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def to_response(self) -> Response:
        return Response(http_status_code=self.status_code, body={
            "error": {
                "code": self.status_code.code,
                "message": self.message
            }
        })
