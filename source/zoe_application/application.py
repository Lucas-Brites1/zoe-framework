from zoe_http.request import Request
from zoe_http.response import Response
from zoe_router.router import Router
from zoe_http.handler import Handler
from zoe_http.middleware import Middleware
from zoe_http.code import HttpCode
from zoe_schema.model_schema import Model

import inspect
import typing

class Zoe:
    def __init__(self: "Zoe", application_name: str) -> None:
        self.__routers: list[Router] = []
        self.__middlewares: list[Middleware] = []
        self._application_name = application_name

    def use_middleware(self, middleware: Middleware) -> None:
        self.__middlewares.append(middleware)

    def include_router(self, router: Router) -> None:
        self.__routers.append(router)

    def _call_handler(self, handler: Handler, request: Request) -> Response:
        hints = {}
        try:
            hints = typing.get_type_hints(
                handler.__call__,
                globalns=vars(inspect.getmodule(type(handler)))
            )
        except Exception as e:
            hints = inspect.get_annotations(handler.__call__)
        
        kwargs = {}
        for param, tipo in hints.items():
          if param in ("return", "request", "self"):
              continue
          if isinstance(tipo, type) and Model.is_model(tipo):
              kwargs[param] = tipo(**request.body)

        return handler(request=request, **kwargs)

    def _resolve(self, request: Request) -> Response:
        def call_handler(req: Request) -> Response:
            for router in self.__routers:
                handler = router.resolve(method=req.method, endpoint=req.route)
                if handler:
                    return self._call_handler(handler=handler, request=req)
            return Response(http_status_code=HttpCode.NOT_FOUND)

        chain = call_handler
        for middleware in reversed(self.__middlewares):
            previous = chain
            def chain(req, m=middleware, p=previous):
                return m(req, p)

        return chain(request)