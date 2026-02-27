from zoe_router.route import Route
from zoe_router.routes import Routes
from zoe_http.method import HttpMethod
from zoe_http.handler import Handler
from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_application.handler_invoker import HandlerInvoker
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException, HttpCode
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

    def __handle_wildcard_route(self, route: Route, requested_endpoint: str, requested_method: HttpMethod) -> tuple[Handler, dict] | None:
        if "*" in route.endpoint:
            wildcard_prefix: str = route.endpoint.replace("*", "")
            full_prefix = self.__prefix + wildcard_prefix
            if requested_endpoint.startswith(full_prefix) and route.method == requested_method:
                wildcard_value = requested_endpoint[len(full_prefix):].lstrip("/")
                return route.handler, {"wildcard": wildcard_value}
        return None
                

    def __match_route(self, method: HttpMethod, endpoint: str) -> tuple[Handler | None, dict, bool]:
        endpoint_exists: bool = False

        for route in self.__assigned_routes:
            full_path_normalized:str = self.__normalize_trailing_slash(full_path=self.__prefix + route.endpoint)

            if "*" in full_path_normalized:
                result = self.__handle_wildcard_route(
                    route=route,
                    requested_endpoint=endpoint,
                    requested_method=method
                )

                if result:
                    handler, params = result
                    return handler, params, False
                continue

            matched, params = self.__match_path(pattern=full_path_normalized, endpoint=endpoint)
            
            if matched and route.method == method:
                return route.handler, params, False
            elif matched and route.method != method:
                endpoint_exists = True

        return None, {}, endpoint_exists

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
        # [static_routes, parametrized_routes, wildcard_routes]
        if not self.__already_reordered:
            self.assigned_routes.prioritize_static_routes()
            self.__already_reordered = True

    def __normalize_trailing_slash(self: "Router", full_path: str) -> str:
        if len(full_path) > 1 and full_path.endswith("/"):
            return full_path[:-1]
        return full_path


    def resolve(self, method: HttpMethod, request: Request) -> Response | None:
        self.__prioritize_static_routes()

        endpoint: str = request.route
        handler, params, method_not_allowed = self.__match_route(method=method, endpoint=self.__normalize_trailing_slash(full_path=endpoint))

        if handler is None:
          if method_not_allowed:
              return ZoeHttpException(
                  message=f"Method {method.value} not allowed for {endpoint}.",
                  status_code=HttpCode.METHOD_NOT_ALLOWED
              ).to_response()
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

    @property
    def prefix(self) -> str:
        return self.__prefix
