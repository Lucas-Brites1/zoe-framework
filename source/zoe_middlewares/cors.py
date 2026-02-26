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

    def __create_response_with_allow_headers(self, origin: str) -> Response:
        prefix: str = "Access-Control-Allow"
        response: Response =  Response(
            http_status_code=HttpCode.OK,
            headers={
                f"{prefix}-Origin": origin or "*",
                f"{prefix}-Methods": ", ".join([m.value for m in self.__allowed_methods]),
                f"{prefix}-Headers": ", ".join(self.__allowed_headers),
                f"{prefix}-Max-Age": "86400"
            }
        )
        return response

    def __call__(self, request: Request, next: Callable) -> Response:
        origin: str = request.headers.get("Origin", "")
        who_is_allowed: str = "*" in self.__allowed_origins or origin in self.__allowed_origins

        if request.method == HttpMethod.OPTIONS:
            if who_is_allowed:
                return self.__create_response_with_allow_headers(origin=origin)
            return Response(http_status_code=HttpCode.OK)

        response = next(request)
        if who_is_allowed:
            response.add_header(key="Access-Control-Allow-Origin", value=origin or "*")
        return response
