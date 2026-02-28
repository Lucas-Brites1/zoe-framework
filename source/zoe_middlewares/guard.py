from zoe_http.middleware import Middleware
from zoe_http.response import Response
from zoe_http.request import Request
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.code import HttpCode
from zoe_middlewares.guard_strategy import GuardStrategy
from zoe_application.zoe_metadata import ZoeMetadata

from typing import Callable

class Guard:
    def __init__(self: "Guard", strategy: GuardStrategy, unauthorized_message: str = "Unauthorized"):
        """
        Middleware that protects routes from unauthorized access.
        ---
        Intercepts every request and delegates validation to a `GuardStrategy`.
        If the strategy returns `False`, the request is blocked and a
        `401 Unauthorized` response is returned before the handler is called.

        Best practice is to attach `Guard` to a specific `Router` so only
        those routes are protected — but it can also be attached globally
        to `App` if the entire API is private.

        ---

        *Args:*
        - `strategy` *(GuardStrategy)* — Authentication strategy used to validate
          the request. Can be any built-in strategy or a custom implementation.
          See the documentation for available built-in strategies:
          `BearerStrategy`, `BasicStrategy`, `ApiKeyStrategy`, `AnyStrategy`, `AllStrategy`.
        - `unauthorized_message` *(str)* — Message returned when the request is blocked.
          Defaults to `"Unauthorized."`.

        ---
        *Example:*
        ```python
        from zoe import Guard, BearerStrategy, Router

        # protect only the admin router
        admin_router = Router("/admin")
        admin_router.use(Guard(BearerStrategy(token="secret")))

        # protect the entire application
        app.use(Guard(ApiKeyStrategy(key="secret")))

        # accept Bearer OR ApiKey
        app.use(Guard(AnyStrategy([
            BearerStrategy(token="secret"),
            ApiKeyStrategy(key="key123")
        ])))
        ```
        """
        self.__strategy: GuardStrategy = strategy
        self.__message = unauthorized_message

    def process(self: "Guard", request: Request, next: Callable) -> Response:
      if not self.__strategy.guard(request):
            return ZoeHttpException(
                message=self.__message,
                status_code=HttpCode.UNAUTHORIZED
            ).to_response()
      return next(request)
