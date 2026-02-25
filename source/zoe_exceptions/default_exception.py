from zoe_http.response import Response
from zoe_http.code import HttpCode

class DefaultException(Exception):
  def __init__(self: "DefaultException", exception_message: str) -> None:
    super().__init__(exception_message)
    self.exception_message = exception_message

  def to_response(self: "DefaultException") -> Response:
    return Response(http_status_code=HttpCode.BAD_REQUEST, body={
      "error": {
          "message": self.exception_message
      }
    })

