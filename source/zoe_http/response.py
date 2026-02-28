from typing import Any

from zoe_http.code import HttpCode

class Response:
    def __init__(self, http_code: HttpCode, headers: dict[str,Any ] | None = None) -> None:
        self.__http_version: str = "HTTP/1.1"
        self.__status_code = http_code
        self.__headers: dict[str, str] = dict(headers) if headers else {}

    @property
    def status_code(self) -> HttpCode:
        return self.__status_code

    def add_header(self, key: str, value: str) -> "Response":
        self.__headers[key] = value
        return self

    def _build(self) -> bytes:
        response_message = self._status_line()
        response_message = self._apply_headers_to_response(response_str=response_message)
        return response_message.encode("utf-8")

    def _status_line(self) -> str:
        return f"{self.__http_version} {self.__status_code.code} {self.__status_code.message}" + "\r\n"

    def _content_line(self, content_type: str, body: str) -> str:
        encoded = body.encode("utf-8")
        content_line: str = ""
        content_line += f"Content-Type: {content_type}\r\n"
        content_line += f"Content-Length: {len(encoded)}\r\n"
        return content_line + "\r\n"

    def _apply_headers_to_response(self, response_str: str) -> str:
        for header_name, header_value in self.__headers.items():
          response_str += f"{header_name}: {header_value}\r\n"
        return response_str + "\r\n"

    @classmethod
    def json(cls, http_code: HttpCode, body: Any, headers: dict | None = None) -> "Json": # type: ignore
        from zoe_http._response_util.response_json import Json
        return Json(http_code=http_code, body=body, headers=headers)

    @classmethod
    def text(cls, http_code: HttpCode, body: Any, charset: str = "utf-8", headers: dict | None = None) -> "PlainText": # type: ignore
      from zoe_http._response_util.response_text import PlainText
      return PlainText(http_code=http_code, text=body, charset=charset, headers=headers)

    @classmethod
    def html(cls, http_code: HttpCode, body: Any, charset: str = "utf-8", headers: dict | None = None) -> "Html": # type: ignore
        from zoe_http._response_util.response_html import Html
        return Html(http_code=http_code, html_content=body, charset=charset, headers=headers)

    @classmethod
    def redirect(cls, redirect_to: str, http_code: HttpCode = HttpCode.FOUND, headers: dict | None = None) -> "Redirect": # type: ignore
        from zoe_http._response_util.response_redirect import Redirect
        return Redirect(http_code=http_code, redirect_to=redirect_to, headers=headers)
