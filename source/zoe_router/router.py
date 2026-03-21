from zoe_router.route import Route
from zoe_router.routes import Routes
from zoe_http.method import HttpMethod
from zoe_http.handler import Handler
from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http._handler_util.handler_invoker import HandlerInvoker
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException, HttpCode
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_http._handler_util.handler_factory import GenericHandlerFactory
from zoe_http._handler_util.handler_validator import HandlerValidator

from typing import overload, Callable
from inspect import isfunction, ismethod, isclass
import re

class Router:
    def __init__(self, prefix: str) -> None:
        if not prefix.startswith("/"):
            prefix = f"/{prefix}"

        self.__prefix = prefix
        self.__assigned_routes: Routes = Routes()
        self.__router_middlewares: list[Middleware] = []
        self.__already_reordered: bool = False
        self.__compiled_routes: dict[str, tuple[re.Pattern, list[str]]] = {}

    def add(self, route: Route) -> None:
        self.__assigned_routes.add(route=route)

    def use(self, middleware: Middleware) -> "Router":
        self.__router_middlewares.append(middleware)
        return self

    def __get_compiled_pattern(self, full_path: str) -> tuple[re.Pattern, list[str]]:
        if full_path in self.__compiled_routes:
          return self.__compiled_routes[full_path]

        param_names = re.findall(r"\{(\w+)\}", full_path)
        regex = re.sub(r"\{\w+\}", r"([^/]+)", full_path)
        compiled = re.compile(f"^{regex}$")

        self.__compiled_routes[full_path] = (compiled, param_names)
        return compiled, param_names

    def __match_path(self, pattern: str, endpoint: str) -> tuple[bool, dict]:
        compiled, param_names = self.__get_compiled_pattern(pattern)
        match = compiled.match(endpoint)
        if not match:
            return False, {}
        return True, dict(zip(param_names, match.groups()))

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
            full_path_normalized: str = self.__normalize_path(path=self.__prefix + route.endpoint)

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

    async def __exec_middlewares(self, request: Request, handler: Handler, params: dict) -> Response:
      async def final(req: Request) -> Response:
          return await HandlerInvoker.invoke(handler=handler, request=req)

      pipeline = final
      for middleware in reversed(self.__router_middlewares):
          current = pipeline
          def make_next(m, n):
              async def next_fn(req):   # ← async aqui dentro
                  return await m.process(req, n)
              return next_fn
          pipeline = make_next(middleware, current)

      return await pipeline(request)

    def __prioritize_static_routes(self) -> None:
        if not self.__already_reordered:
            self.__assigned_routes.prioritize_static_routes()
            self.__already_reordered = True

    def __normalize_path(self, path: str) -> str:
      if not path.startswith("/"):
          path = f"/{path}"
      if len(path) > 1 and path.endswith("/"):
          path = path[:-1]
      path = path.replace("//", "/")
      return path

    async def resolve(self, method: HttpMethod, request: Request) -> Response | None:
        self.__prioritize_static_routes()

        endpoint: str = self.__normalize_path(path=request.route)
        request._set_normalized_route(endpoint)

        handler, params, method_not_allowed = self.__match_route(method=method, endpoint=endpoint)

        if handler is None:
            if method_not_allowed:
                return ZoeHttpException(
                    message=f"Method {method.value} not allowed for {endpoint}.",
                    status_code=HttpCode.METHOD_NOT_ALLOWED
                ).to_response()
            return None

        request.set_path_params(params)

        if not self.__router_middlewares:
            return await HandlerInvoker.invoke(handler=handler, request=request)

        return await self.__exec_middlewares(request=request, handler=handler, params=params)

    @overload
    def post(self, endpoint: str, handler: Handler) -> "Router": ...
    @overload
    def post(self, endpoint: str) -> Callable[[Callable], Handler]: ...

    def post(self, endpoint: str, handler: Handler | None = None) -> "Router | Callable[[Callable], Handler]":
        if handler:
            self.__assigned_routes.add(Route.post(endpoint=endpoint, handler=handler))
            return self

        def post_deco(fn_wrapped: Callable | Handler) -> Handler:
            handler_generated_by_factory: Handler = self.__wrap_handler(fn_wrapped)
            self.__assigned_routes.add(Route.post(endpoint=endpoint, handler=handler_generated_by_factory))
            return handler_generated_by_factory
        return post_deco  # type: ignore

    @overload
    def get(self, endpoint: str, handler: Handler) -> "Router": ...
    @overload
    def get(self, endpoint: str) -> Callable[[Callable], Handler]: ...

    def get(self, endpoint: str, handler: Handler | None = None) -> "Router | Callable[[Callable], Handler]":
        if handler:
            self.__assigned_routes.add(Route.get(endpoint=endpoint, handler=handler))
            return self

        def get_deco(fn_wrapped: Callable | Handler) -> Handler:
            handler_generated_by_factory: Handler = self.__wrap_handler(fn_wrapped)
            self.__assigned_routes.add(Route.get(endpoint=endpoint, handler=handler_generated_by_factory))
            return handler_generated_by_factory
        return get_deco  # type: ignore

    @overload
    def put(self, endpoint: str, handler: Handler) -> "Router": ...
    @overload
    def put(self, endpoint: str) -> Callable[[Callable], Handler]: ...

    def put(self, endpoint: str, handler: Handler | None = None) -> "Router | Callable[[Callable], Handler]":
        if handler:
            self.__assigned_routes.add(Route.put(endpoint=endpoint, handler=handler))
            return self

        def put_deco(fn_wrapped: Callable | Handler) -> Handler:
            handler_generated_by_factory: Handler = self.__wrap_handler(fn_wrapped)
            self.__assigned_routes.add(Route.put(endpoint=endpoint, handler=handler_generated_by_factory))
            return handler_generated_by_factory
        return put_deco  # type: ignore

    @overload
    def patch(self, endpoint: str, handler: Handler) -> "Router": ...
    @overload
    def patch(self, endpoint: str) -> Callable[[Callable], Handler]: ...

    def patch(self, endpoint: str, handler: Handler | None = None) -> "Router | Callable[[Callable], Handler]":
        if handler:
            self.__assigned_routes.add(Route.patch(endpoint=endpoint, handler=handler))
            return self

        def patch_deco(fn_wrapped: Callable | Handler) -> Handler:
            handler_generated_by_factory: Handler = self.__wrap_handler(fn_wrapped)
            self.__assigned_routes.add(Route.patch(endpoint=endpoint, handler=handler_generated_by_factory))
            return handler_generated_by_factory
        return patch_deco  # type: ignore

    @overload
    def delete(self, endpoint: str, handler: Handler) -> "Router": ...
    @overload
    def delete(self, endpoint: str) -> Callable[[Callable], Handler]: ...

    def delete(self, endpoint: str, handler: Handler | None = None) -> "Router | Callable[[Callable], Handler]":
        if handler:
            self.__assigned_routes.add(Route.delete(endpoint=endpoint, handler=handler))
            return self

        def delete_deco(fn_wrapped: Callable | Handler) -> Handler:
            handler_generated_by_factory: Handler = self.__wrap_handler(fn_wrapped)
            self.__assigned_routes.add(Route.delete(endpoint=endpoint, handler=handler_generated_by_factory))
            return handler_generated_by_factory
        return delete_deco  # type: ignore

    def __wrap_handler(self, fn_or_handler: Handler | Callable) -> Handler:
      if isclass(fn_or_handler):
          try:
              instance = fn_or_handler()
          except Exception as e:
              raise ZoeNonHttpError(
                  why=f"Failed to instantiate handler class '{fn_or_handler.__name__}'",
                  explain=(
                      f"An exception was raised while trying to instantiate '{fn_or_handler.__name__}':\n"
                      f"{e}"
                  ),
                  fix=(
                      f"Make sure '{fn_or_handler.__name__}' can be instantiated without arguments,\n"
                      f"or register it as a dependency in the Container."
                  )
              )

          if not isinstance(instance, Handler):
              raise ZoeNonHttpError(
                  why=f"Class '{fn_or_handler.__name__}' is not a Handler subclass",
                  explain=f"'{fn_or_handler.__name__}' must extend Handler to be used as a class-based handler.",
                  fix=f"class {fn_or_handler.__name__}(Handler):\n    def handle(self, ...) -> Response: ..."
              )

          return instance

      if isinstance(fn_or_handler, Handler):
          HandlerValidator.validate_signature(fn_or_handler.handle)
          return fn_or_handler

      if isfunction(fn_or_handler) or ismethod(fn_or_handler):
          return GenericHandlerFactory.new(fn=fn_or_handler)

      raise ZoeNonHttpError(
          why=f"Invalid handler type '{type(fn_or_handler).__name__}'",
          explain=(
              f"Expected a Handler instance, a Handler subclass, or a function.\n"
              f"Received: {type(fn_or_handler).__name__}"
          ),
          fix=(
              f"Use one of the supported handler formats:\n\n"
              f"  @router.get('/endpoint')\n"
              f"  def my_handler(req: Request) -> Response: ...\n\n"
              f"  or:\n\n"
              f"  class MyHandler(Handler):\n"
              f"      def handle(self, req: Request, ...) -> Response: ..."
          )
      )

    @property
    def assigned_routes(self) -> Routes:
        return self.__assigned_routes

    @property
    def router_middlewares(self) -> list[Middleware]:
        return self.__router_middlewares

    @property
    def prefix(self) -> str:
        return self.__prefix
