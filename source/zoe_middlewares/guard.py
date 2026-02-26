from zoe_http.middleware import Middleware
from zoe_http.response import Response
from zoe_http.request import Request
from zoe_router.router import Routes, Route, Router

from typing import Callable

class GuardStrategy:
    @staticmethod
    def bearer() -> str:
        return "Bearer"

    @staticmethod
    def apikey() -> str:
        return "ApiKey"

    @staticmethod
    def basic() -> str:
        return "Basic"

class Guard(Middleware):
    def __init__(self: "Guard", routes: Routes, strategy: GuardStrategy):
        self.__routes = routes
        self.__strategy: str = strategy

    def __call__(self: "Guard", request: Request, next: Callable) -> Response:
        for route in self.__routes:
            r_route_full: str = f"{request.route}{request.method}"
            route_full: str = f"{route.endpoint}{route.method}"
            if route_full == r_route_full:
