from typing import Any
import json

from zoe_http.code import HttpCode

class Response:
    def __init__(self: "Response", http_status_code: HttpCode, body: Any = None) -> None:
        self.__status_code = http_status_code
        self.__body = body
        self.__http_version: str = "HTTP/1.1"

    @property
    def status_code(self: "Response") -> HttpCode:
        return self.__status_code

    def __status_line(self) -> str:
        return f"{self.__http_version} {self.__status_code.code} {self.__status_code.message}\r\n"

    def _build(self, *headers: dict[str, Any]) -> bytes:
        response_message = self.__status_line()
        
        body_data = None
        if self.__body is not None:
            body_data = self.__serialize(self.__body)
            body_json = json.dumps(body_data)
            response_message += f"Content-Type: application/json\r\n"
            response_message += f"Content-Length: {len(body_json.encode('utf-8'))}\r\n"

        for header in headers:
            for k, v in header.items():
                response_message += f"{k}: {v}\r\n"

        response_message += "\r\n"
        if body_data is not None:
            response_message += body_json

        return response_message.encode("utf-8")

    def __serialize(self: "Response", obj: Any) -> Any:
        if hasattr(obj, 'to_dict'):
            return self.__serialize(obj=obj.to_dict())
        elif isinstance(obj, dict):
            return {k: self.__serialize(v) for k,v in obj.items()}
        elif isinstance(obj, list):
            return [self.__serialize(i) for i in obj]
        return obj