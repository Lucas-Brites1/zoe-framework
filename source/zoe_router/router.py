from zoe_router.route import Route
from zoe_router.routes import Routes
from zoe_http.method import HttpMethod
from zoe_http.handler import Handler
from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_application.handler_invoker import HandlerInvoker
import re

class Router:
    def __init__(self, prefix: str) -> None:
        self.__assigned_routes: Routes = Routes()
        self.__prefix = prefix
        self.__router_middlewares: list[Middleware] = []
        self.__already_reordered: bool = False

    def add(self, route: Route) -> None:
        self.__assigned_routes.add(route=route)

    def use(self, middleware: Middleware) -> "Router":
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

    def __match_route(self, method: HttpMethod, endpoint: str) -> tuple[Handler | None, dict]:
        for route in self.__assigned_routes:
            full = self.__prefix + route.endpoint
            matched, params = self.__match_path(pattern=full, endpoint=endpoint)
            if route.method.value == method.value and matched:
                return route.handler, params
        return None, {}

    def __exec_middlewares(self, request: Request, handler: Handler, params: dict) -> Response:
        def final(req: Request) -> Response:
            return HandlerInvoker.invoke(handler=handler, request=req)

        pipeline = final
        for middleware in reversed(self.__router_middlewares):
            current = pipeline
            def make_next(m, n):
                return lambda req: m(req, n)
            pipeline = make_next(middleware, current)

        return pipeline(request)

    def __prioritize_static_routes(self) -> None:
        if not self.__already_reordered:
            self.assigned_routes.prioritize_static_routes()
            self.__already_reordered = True

    def resolve(self, method: HttpMethod, endpoint: str, request: Request) -> Response | None:
        self.__prioritize_static_routes()
        handler, params = self.__match_route(method=method, endpoint=endpoint)

        if handler is None:
            return None

        request.set_path_params(params)
        if not self.__router_middlewares:
            return HandlerInvoker.invoke(handler=handler, request=request)

        return self.__exec_middlewares(request=request, handler=handler, params=params)

    def POST(self, endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.post(endpoint=endpoint, handler=handler))
        return self

    def GET(self, endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.get(endpoint=endpoint, handler=handler))
        return self

    def PUT(self, endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.put(endpoint=endpoint, handler=handler))
        return self

    def PATCH(self, endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.patch(endpoint=endpoint, handler=handler))
        return self

    def DELETE(self, endpoint: str, handler: Handler) -> "Router":
        self.__assigned_routes.add(Route.delete(endpoint=endpoint, handler=handler))
        return self

    @property
    def assigned_routes(self) -> Routes:
        return self.__assigned_routes

    @property
    def router_middlewares(self) -> list[Middleware]:
        return self.__router_middlewares
