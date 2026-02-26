from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_http.method import HttpMethod
from typing import Callable

class CORS(Middleware):
    def __init__(self, allowed_origins: list[str] = ["*"], allowed_methods: list[HttpMethod] = None, allowed_headers: list[str] = None):
        self.__allowed_origins = allowed_origins
        self.__allowed_methods = allowed_methods or [
            HttpMethod.GET, HttpMethod.POST, HttpMethod.PUT,
            HttpMethod.PATCH, HttpMethod.DELETE, HttpMethod.OPTIONS
        ]
        self.__allowed_headers = allowed_headers or [
            "Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"
        ]

    def __add_headers(self, response: Response, origin: str) -> None:
        response.add_header("Access-Control-Allow-Origin", origin or "*")
        response.add_header("Access-Control-Allow-Methods", ", ".join([m.value for m in self.__allowed_methods]))
        response.add_header("Access-Control-Allow-Headers", ", ".join(self.__allowed_headers))
        response.add_header("Access-Control-Max-Age", "86400")

    def __call__(self, request: Request, next: Callable) -> Response:
        origin: str = request.headers.get("Origin", "")
        who_is_allowed: str = "*" in self.__allowed_origins or origin in self.__allowed_origins

        if request.method == HttpMethod.OPTIONS:
            response = Response(HttpCode.OK)
            if who_is_allowed:
                self.__add_headers(response=response, origin=origin)
            return response

        response = next(request)
        if who_is_allowed:
            self.__add_headers(response=response, origin=origin)
        return response
