from urllib.parse import unquote
from zoe_http.method import HttpMethod
from zoe_http._request_util.query_params import QueryParams
from zoe_http._request_util.path_params import PathParams
from zoe_http._request_util.form_params import FormParams
from zoe_http._request_util.request_body import Body
from zoe_http._request_util.request_multipart import Multipart
from zoe_http._request_util.request_auth import Auth
from zoe_http._request_util.request_headers import RequestHeaders
from zoe_http._request_util.request_state import RequestState
from zoe_exceptions.http_exceptions.exc_malformed_request import MalformedRequestException

class Request:
    def __init__(self: "Request", headers: RequestHeaders, body_bytes: bytes, client_ip: str) -> None:
        self.__client_ip = client_ip
        self.__body_bytes = body_bytes

        self.__header: RequestHeaders = headers
        self.__method: HttpMethod
        self.__route: str
        self.__http_version: str
        self.__parse_request_line(self.__header._request_line)

        self.__form_params = FormParams()
        self.__query_params = QueryParams()
        self.__path_params = PathParams()
        self.__body: Body = Body.empty()
        self.__multipart: Multipart = Multipart.empty()

        if self.__header.content_type is not None:
          if "multipart/form-data" in self.__header.content_type:
            self.__multipart = Multipart.from_request(
                content_type=self.__header.content_type,
                body_bytes=self.__body_bytes
            )
          else:
            self.__body: Body = Body.from_request(
                content_type=self.__header.content_type,
                body_bytes=self.__body_bytes
            )

        self.__auth: Auth = Auth(
            authorization_header=self.headers.authorization
        )

        self.__state: RequestState = RequestState()

    @property
    def body(self: "Request") -> Body:
        return self.__body

    @property
    def multipart(self: "Request") -> Multipart:
        return self.__multipart

    @property
    def method(self: "Request") -> HttpMethod:
        return self.__method

    @property
    def route(self: "Request") -> str:
        return self.__route

    @property
    def headers(self: "Request") -> "RequestHeaders":
        return self.__header

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

    @property
    def auth(self: "Request") -> Auth:
        return self.__auth

    @property
    def state(self: "Request") -> RequestState:
        return self.__state

    def set_path_params(self: "Request", params: dict) -> None:
        for k, v in params.items():
            self.__path_params._set_param(k, unquote(v))

    def __parse_query_params(self: "Request", query_string: str) -> None:
        for param in query_string.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                self.__query_params._set_param(key=key, value=unquote(value))

    def __parse_request_line(self, request_raw_part: str) -> "Request":
        (method, full_path, http_version) = request_raw_part.split(" ")

        if not method or not full_path or not http_version:
            raise MalformedRequestException("invalid request line format.")

        full_path_normalized: str = full_path
        if len(full_path) > 1 and full_path.endswith("/"):
            full_path_normalized = full_path[:-1]

        if "?" in full_path_normalized:
            self.__route, query_string = full_path.split("?", 1)
            self.__parse_query_params(query_string)
        else:
            self.__route = full_path_normalized

        self.__method = HttpMethod.str_to_method(method_str=method)
        self.__http_version = http_version
        return self

    def _set_normalized_route(self, route: str) -> None:
        self.__route = route
