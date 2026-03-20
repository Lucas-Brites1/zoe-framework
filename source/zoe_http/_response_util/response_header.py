from zoe_http._response_util.response_cookies import ResponseCookie
from typing import Any
from datetime import datetime, timezone
import uuid

class ResponseHeader:
  def __init__(self, headers: dict[str, str] | None = None) -> None:
    self.__headers: dict[str, Any] = {
          "Date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
          "X-Powered-By": "Zoe",
          "X-Request-ID": f"{uuid.uuid4()}",
          **(dict(headers) if headers else {})
        }
    self.__cokies: ResponseCookie = ResponseCookie()

  @property
  def cookies(self) -> "ResponseCookie":
     return self.__cokies

  def add(self, key: str, value: str) -> "ResponseHeader":
     self.__headers[key] = value
     return self

  def _build(self, to_append: str) -> str:
    for header_name, header_value in self.__headers.items():
        to_append += f"{header_name}: {header_value}\r\n"

    to_append = self.__cokies._build(to_append=to_append)
    return to_append + "\r\n"
