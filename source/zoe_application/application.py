from zoe_http.request import Request
from zoe_http.response import Response
from zoe_router.router import Router
from zoe_http.handler import Handler
from zoe_http.code import HttpCode
from zoe_schema.model_schema import Model

import inspect

class Zoe:
  def __init__(self: "Zoe") -> None:
    self.__routers: list[Router] = []
    #self.__middlewares: list[Middleware] = []

  def _call_handler(self: "Zoe", handler: Handler, request: Request) -> Response:
    hints = inspect.get_annotations(handler.__call__)
    kwargs = {}
    for param, type in hints.items():
      if param in ("return", "request"):
        continue
      try:
        if issubclass(type, Model):
          kwargs[param] = type(**request.body)
      except TypeError:
        pass

    return handler(request=request, kwargs=kwargs)

  def _resolve(self: "Zoe", request: Request) -> Response:
    #for middleware in middlewares:
      #middleware(request, lambda r:r)

    for router in self.__routers:
      handler: Handler = router.resolve(method=request.method, endpoint=request.route)
      if handler:
        return self._call_handler(handler=handler, request=request)

    return Response(http_status_code=HttpCode.NOT_FOUND)
