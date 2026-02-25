from zoe_http.request import Request
from zoe_http.response import Response
from zoe_router.router import Router
from zoe_http.handler import Handler
from zoe_router.router import Route, Routes, Router
from zoe_http.middleware import Middleware
from zoe_application.handler_invoker import HandlerInvoker
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.http_exceptions.exc_not_found import RouteNotFoundException

class Zoe:
    def __init__(self: "Zoe") -> None:
        self.__base_router: Router = Router(prefix="")
        self.__routers: list[Router] = [self.__base_router]
        self.__middlewares: list[Middleware] = []

    def use(self: "Zoe", to_add: Route | Routes | Router | Middleware) -> "Zoe":
        match type(to_add).__name__:
            case "Route":
                self.__base_router.add(route=to_add)
            case "Routes":
                for route in to_add:
                    self.__base_router.add(route=route)
            case "Router":
                self.__routers.append(to_add)
            case "Middleware":
                self.__middlewares.append(to_add)
            case _:
                if hasattr(to_add, '__call__') and not isinstance(to_add, (Route, Routes, Router)):
                    self.__middlewares.append(to_add)
                else:
                    raise TypeError(f"Cannot register type '{type(to_add).__name__}'")
        return self

    def _call_handler(self, handler: Handler, request: Request) -> Response:
      return HandlerInvoker.invoke(handler=handler, request=request)

    def _resolve(self, request: Request) -> Response:
        def call_handler(req: Request) -> Response:
            for router in self.__routers:
                (handler, params) = router.resolve(method=req.method, endpoint=req.route)
                if handler:
                    request.set_path_params(params=params)
                    return self._call_handler(handler=handler, request=req)
            return RouteNotFoundException(request=request).to_response()

        chain = call_handler
        for middleware in reversed(self.__middlewares):
            previous = chain
            def chain(req, m=middleware, p=previous):
                return m(req, p)

        try:
            return chain(request)
        except ZoeHttpException as exc:
            return exc.to_response()
        except Exception as exc:
            return InternalServerException(detail=str(exc)).to_response()
