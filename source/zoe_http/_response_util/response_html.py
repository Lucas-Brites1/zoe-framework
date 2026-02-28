from zoe_http.response import Response
from zoe_http.code import HttpCode

from typing import Any

class Html(Response):
  _content_type = "text/html"
  def __init__(self: "Html", http_code: HttpCode, html_content: str, charset: str = "utf-8", headers: dict[str, Any] | None = None) -> None:
    super().__init__(http_code=http_code, headers=headers)
    self._body = html_content
    self._charset = charset

  def _build(self: "Html") -> bytes:
    response_message: str = self._status_line()
    response_message += self._content_line(
      content_type=f"{self._content_type}; charset={self._charset}",
      body=self._body
    )
    response_message = self._apply_headers_to_response(response_str=response_message)
    response_message += self._body

    return response_message.encode(self._charset)
