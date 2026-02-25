from zoe_http.response import Response
from zoe_http.code import HttpCode

class ZoeDefaultException(Exception):
  def __init__(self: "ZoeDefaultException", exception_message: str) -> None:
    super().__init__(exception_message)
    self.exception_message = exception_message

  def to_response(self: "ZoeDefaultException") -> Response:
    return Response(http_status_code=HttpCode.BAD_REQUEST, body={
      "error": {
          "message": self.exception_message
      }
    })

