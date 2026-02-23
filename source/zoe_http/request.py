from typing import Any
import json

from zoe_http.method import HttpMethod

class Request:
    def __init__(self: "Request", raw_data: str) -> None:
        self.__fields: dict[Any, Any] = {}
        self.__raw_data = raw_data
        self.__parse()

        self.__method: HttpMethod
        self.__route: str
        self.__http_version: str
        self.__body: dict | Any

        self.__content_type: str
        self.__content_length: int
        self.__host: str
        self.__headers: dict[str, str] 
        self.__accept: str
        self.__connection: str

    @property
    def body(self: "Request") -> dict | Any:
        return self.__body

    @property
    def method(self: "Request") -> HttpMethod:
        return self.__method

    @property
    def route(self: "Request") -> str:
        return self.__route

    @property
    def headers(self: "Request") -> dict[str, Any]:
        return self.__headers
    
    @property
    def content_type(self: "Request") -> str:
        return self.__content_type
    
    @property
    def content_length(self: "Request") -> int:
        return self.__content_length

    @property
    def host(self: "Request") -> str:
        return self.__host

    @property
    def http_version(self: "Request") -> str:
        return self.__http_version

    def __parse_request_line(self: "Request", request_raw_part: str) -> "Request":
        parts: list[str] = request_raw_part.split(" ")
        self.__method = HttpMethod.str_to_method(method_str=parts[0])
        self.__route = parts[1]
        self.__http_version = parts[2]
        return self

    def __parse_headers(self: "Request", header_raw_part: list[str]) -> "Request":
        self.__headers = {}
        for header in header_raw_part:
            key, _, value = header.partition(": ")
            match key:
                case "Host":
                    self.__host = value
                case "Content-Type":
                    self.__content_type = value
                case "Content-Length":
                    self.__content_length = int(value)
                case "Accept":
                    self.__accept = value
                case "Connection":
                    self.__connection = value
                case _:
                    self.__headers[key] = value
        return self
        
    def __parse_body(self: "Request", body_raw_part: str) -> "Request":
        try:
            self.__body = json.loads(body_raw_part)
        except Exception as exc:
            raise Exception(f"Malformed request body '{body_raw_part}'\n{exc}")

    def __parse(self: "Request") -> None:
        splitted_data: list[str] = self.__raw_data.split("\r\n")
        empty_line_index:int = splitted_data.index("")
        body_raw:str = "\r\n".join(splitted_data[empty_line_index + 1:]) 

        self.__parse_request_line(request_raw_part=splitted_data[0])\
        .__parse_headers(header_raw_part=splitted_data[1:empty_line_index])\
        .__parse_body(body_raw_part=body_raw)