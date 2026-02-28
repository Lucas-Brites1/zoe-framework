from zoe_http.response import Response
from zoe_http.code import HttpCode

from typing import Any

class PlainText(Response):
  _content_type = "text/plain"
  def __init__(self: "PlainText", http_code: HttpCode, text: Any, charset: str = "utf-8", headers: dict[str, Any] | None = None):
    super().__init__(http_code, headers)
    self._body = text
    self._charset = charset

  def _build(self: "PlainText") -> bytes:
    response_message: str = ""
    response_message = self._status_line()

    response_message += self._content_line(content_type=self._content_type,body=self._body)
    response_message = self._apply_headers_to_response(response_str=response_message)
    try:
      response_message += str(self._body)
    except Exception as exc:
      raise exc

    return response_message.encode(encoding=self._charset)
