from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_http.bytes import Bytes
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from typing import Callable

class BodyLimiter(Middleware):
    def __init__(self, max_size: Bytes = Bytes.from_mb(n=1)) -> None:
        """
        Middleware that limits the maximum allowed request body size.
        ---
        Protects the server against payload flooding and resource exhaustion attacks,
        where malicious clients send oversized request bodies to consume memory and CPU.
        If the request body exceeds the limit, the server responds with
        `413 Payload Too Large` before the handler is ever called.

        ---

        *Args:*
        - `max_size` *(Bytes)* — Maximum allowed body size. Must be a `Bytes` instance.
        Use `Bytes.from_kb()` or `Bytes.from_mb()` to build the value.
        Defaults to `Bytes.from_mb(1)` *(1 MB)*.

        ---

        *Example:*
        ```python
            from zoe import BodyLimiter, Bytes

            # default — rejects bodies larger than 1MB
            app.use(BodyLimiter())

            # custom — rejects bodies larger than 500KB
            app.use(BodyLimiter(max_size=Bytes.from_kb(500)))

            # custom — rejects bodies larger than 3MB
            app.use(BodyLimiter(max_size=Bytes.from_mb(3)))
        ```
        """
        self.__max_size: Bytes = max_size
    
    def __call__(self: "BodyLimiter", request: Request, next: Callable) -> Response:
        if request.content_length > self.__max_size.value:
            return ZoeHttpException(
                message=f"Payload too large. Maximum allowed size is {self.__max_size.value} bytes",
                status_code=HttpCode.PAYLOAD_TOO_LARGE
            ).to_response()
        return next(request)