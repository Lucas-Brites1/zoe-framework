from zoe_http.response import Response
from zoe_http.code import HttpCode

from typing import Any

class Redirect(Response):
  def __init__(self: "Redirect", http_code: HttpCode, redirect_to: str, headers: dict[str, Any] | None = None) -> None:
    super().__init__(http_code=http_code, headers=headers)
    self._redirect_to = redirect_to

  def _build(self) -> bytes:
    response_message = self._status_line()

    self.headers.add("Location", self._redirect_to)
    self.headers.add("Content-Length", "0")
    
    response_message = self.headers._build(to_append=response_message)

    return response_message.encode("utf-8")
