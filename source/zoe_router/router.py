from zoe_router.route import Route
from zoe_router.routes import Routes
from zoe_http.method import HttpMethod
from zoe_http.handler import Handler
from zoe_http.middleware import Middleware
import re

class Router:
    def __init__(self: "Router", prefix: str) -> None:
        self.__assigned_routes: Routes = Routes()
        self.__prefix = prefix
        self.__router_middlewares: list[Middleware] = []

    def add(self: "Router", route: Route) -> None:
        self.__assigned_routes.add(route=route)

    def use(self: "Router", middleware: Middleware) -> "Router":
        self.__router_middlewares.append(middleware)
        return self

    def __match_path(self, pattern: str, endpoint: str) -> tuple[bool, dict]:
            pattern_parts = pattern.split("/")
            endpoint_parts = endpoint.split("/")

            if len(pattern_parts) != len(endpoint_parts):
                return False, {}

            params = {}
            for p, a in zip(pattern_parts, endpoint_parts):
                if re.match(r"^\{\w+\}$", p):
                    params[p[1:-1]] = a
                elif p != a:
                    return False, {}

            return True, params

    def resolve(self, method: HttpMethod, endpoint: str) -> tuple[Handler | None, dict]:
        for route in self.__assigned_routes:
            full = self.__prefix + route.endpoint
            matched, params = self.__match_path(pattern=full, endpoint=endpoint)
            if route.method.value == method.value and matched:  
                return route.handler, params
        return None, {}

    def POST(self: "Router", endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.post(endpoint=endpoint, handler=handler))
        return self

    def GET(self: "Router", endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.get(endpoint=endpoint, handler=handler))
        return self

    def PUT(self: "Router", endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.put(endpoint=endpoint, handler=handler))
        return self

    def PATCH(self: "Router", endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.patch(endpoint=endpoint, handler=handler))
        return self

    def DELETE(self: "Router", endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.delete(endpoint=endpoint, handler=handler))
        return self

    @property
    def assigned_routes(self: "Router") -> Routes:
        return self.__assigned_routes

    @property
    def prefix(self: "Router") -> str:
        return self.__prefix
