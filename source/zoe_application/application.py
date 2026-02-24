from zoe_http.request import Request
from zoe_http.response import Response
from zoe_router.router import Router
from zoe_http.handler import Handler
from zoe_router.router import Route, Routes, Router
from zoe_http.middleware import Middleware
from zoe_http.code import HttpCode
from zoe_schema.model_schema import Model
from zoe_exceptions.schemas_exceptions.validation_exception import ValidatorException
from zoe_exceptions.schemas_exceptions.schema_unexpected_type import SchemaFieldUnexpectedType

import inspect
import typing

class Zoe:
    def __init__(self: "Zoe", application_name: str) -> None:
        self.__base_router: Router = Router(prefix="")
        self.__routers: list[Router] = [self.__base_router]
        self.__middlewares: list[Middleware] = []
        self._application_name = application_name

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
            try:
                kwargs[param] = tipo(**request.body)
            except ValidatorException as e:
                return e.to_response(model_name=tipo.__name__)
            except SchemaFieldUnexpectedType as e:
                return e.to_response(model_name=tipo.__name__)
            except Exception as e:
                print(f"Outra exception: {type(e).__name__}: {e}")
        return handler(request=request, **kwargs)

    def _resolve(self, request: Request) -> Response:
        def call_handler(req: Request) -> Response:
            for router in self.__routers:
                (handler, params) = router.resolve(method=req.method, endpoint=req.route)
                if handler:
                    request.set_path_params(params=params)
                    return self._call_handler(handler=handler, request=req)
            return Response(http_status_code=HttpCode.NOT_FOUND)

        chain = call_handler
        for middleware in reversed(self.__middlewares):
            previous = chain
            def chain(req, m=middleware, p=previous):
                return m(req, p)

        return chain(request)