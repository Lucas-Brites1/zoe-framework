from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_http.method import HttpMethod
from typing import Callable

class CORS:
    def __init__(self, allowed_origins: list[str] = ["*"], allowed_methods: list[HttpMethod] | None = None, allowed_headers: list[str] | None = None):
        """
        Middleware that enables Cross-Origin Resource Sharing (CORS).
        ---
        Allows web applications running on a different origin (domain, port or protocol)
        to access resources from your server. This is enforced by browsers via the
        Same-Origin Policy — without CORS headers, browsers block cross-origin requests
        before they reach your handlers.

        When a browser detects a cross-origin request, it first sends a preflight
        `OPTIONS` request asking for permission. This middleware intercepts that preflight
        and responds with the appropriate headers, allowing the real request to proceed.

        ---

        *Args:*
        - `allowed_origins` *(list[str])* — Origins allowed to access the server.
        An origin is the combination of protocol, domain and port
        (e.g. `http://localhost:3000`). Defaults to `["*"]` *(allow all)*.
        - `allowed_methods` *(list[HttpMethod])* — HTTP methods the client is allowed
        to use. Defaults to all standard methods.
        - `allowed_headers` *(list[str])* — Headers the client is allowed to send.
        Defaults to `["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"]`.

        ---

        *Example:*
        ```python
        from zoe import CORS

        # allow all origins (development)
        app.use(CORS())

        # restrict to specific origins (production)
        app.use(CORS(allowed_origins=["https://mysite.com", "https://www.mysite.com"]))
        ```
        """
        self.__allowed_origins = allowed_origins
        self.__allowed_methods = allowed_methods or [
            HttpMethod.GET, HttpMethod.POST, HttpMethod.PUT,
            HttpMethod.PATCH, HttpMethod.DELETE, HttpMethod.OPTIONS
        ]
        self.__allowed_headers = allowed_headers or [
            "Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"
        ]

    def __create_response_with_allow_headers(self, origin: str) -> Response:
        allow_prefix: str = "Access-Control-Allow"
        response: Response =  Response(
            http_status_code=HttpCode.OK,
            headers={
                f"{allow_prefix}-Origin": origin or "*",
                f"{allow_prefix}-Methods": ", ".join([m.value for m in self.__allowed_methods]),
                f"{allow_prefix}-Headers": ", ".join(self.__allowed_headers),
                f"{allow_prefix}-Max-Age": "86400"
            }
        )
        return response

    def process(self, request: Request, next: Callable) -> Response:
        origin: str = request.headers.get("Origin", "")
        who_is_allowed: str = "*" in self.__allowed_origins or origin in self.__allowed_origins # type: ignore

        if request.method == HttpMethod.OPTIONS:
            if who_is_allowed:
                return self.__create_response_with_allow_headers(origin=origin)
            return Response(http_status_code=HttpCode.OK)

        response = next(request)
        if who_is_allowed:
            response.add_header(key="Access-Control-Allow-Origin", value=origin or "*")
        return response
