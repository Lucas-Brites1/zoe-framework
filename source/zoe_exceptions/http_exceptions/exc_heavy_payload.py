from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.code import HttpCode

class PayloadTooLargeException(ZoeHttpException):
  def __init__(self, message: str | None = None):
    super().__init__(status_code=HttpCode.PAYLOAD_TOO_LARGE, message="Payload too large." if message is None else message)
