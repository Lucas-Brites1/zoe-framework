from typing import Any
import json

from zoe_http.code import HttpCode

class Response:
    def __init__(self: "Response", http_status_code: HttpCode, http_version: str = "HTTP/1.1") -> None:
        self.__status_code = http_status_code
        self.__http_version = http_version

    def __status_line(self: "Response") -> str:
        return f"{self.__http_version} {self.__status_code} {self.__http_message}\r\n"

    def _build(self, body: Any = None, *headers: dict[str, Any]) -> bytes:
        response_message = self.__status_line()
        for header in headers:
            for k, v in header.items():
                response_message += f"{k}: {v}\r\n"
        response_message += "\r\n"
        if body:
            response_message += json.dumps(body)
        return response_message.encode("utf-8")
