from typing import Any
from urllib.parse import unquote
import json

from zoe_http.method import HttpMethod
from zoe_http._request_util.query_params import QueryParams
from zoe_http._request_util.path_params import PathParams
from zoe_http._request_util.form_params import FormParams

class Request:
    def __init__(self: "Request", raw_data: str, client_ip: str) -> None:
        self.__fields: dict[Any, Any] = {}
        self.__client_ip = client_ip
        self.__raw_data = raw_data

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

        self.__form_params = FormParams()
        self.__query_params = QueryParams() #opcional depois de ? -> GET /users?page=1&limit=10&order=asc
        self.__path_params = PathParams() #obrigatorio -> GET /users/123/posts/456

        self.__parse()

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

    @property
    def client_ip(self: "Request") -> str:
        return self.__client_ip

    @property
    def path_params(self: "Request") -> PathParams:
        return self.__path_params
    
    @property
    def query_params(self: "Request") -> QueryParams:
        return self.__query_params
    
    @property
    def form_params(self: "Request") -> FormParams:
        return self.__form_params

    def set_path_params(self: "Request", params: dict) -> None:
        for k, v in params.items():
            self.__path_params[k] = v

    def __parse_query_params(self: "Request", query_string: str) -> None:
        for param in query_string.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                self.__query_params[key] = unquote(value)

    def __parse_request_line(self, request_raw_part: str) -> "Request":
        parts = request_raw_part.split(" ")
        full_path = parts[1]

        if "?" in full_path:
            self.__route, query_string = full_path.split("?", 1)
            self.__parse_query_params(query_string)
        else:
            self.__route = full_path
        
        self.__method = HttpMethod.str_to_method(method_str=parts[0])
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
        
    def __parse_body(self, body_raw_part: str) -> "Request":
        if not body_raw_part.strip():
            self.__body = None
            return self
        try:
            self.__body = json.loads(body_raw_part)
        except Exception as exc:
            raise Exception(f"Malformed request body '{body_raw_part}'\n{exc}")
        return self

    def __parse(self: "Request") -> None:
        splitted_data: list[str] = self.__raw_data.split("\r\n")
        empty_line_index:int = splitted_data.index("")
        body_raw:str = "\r\n".join(splitted_data[empty_line_index + 1:]) 

        self.__parse_request_line(request_raw_part=splitted_data[0])\
        .__parse_headers(header_raw_part=splitted_data[1:empty_line_index])\
        .__parse_body(body_raw_part=body_raw)