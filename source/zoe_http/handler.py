from typing import Any
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException

class Handler:
    def __init__(self: "Handler") -> None:
        self.__request: Request | None = None # type: ignore

    @property
    def request(self: "Handler") -> Request:
        if self.__request is None:
            raise RuntimeError("Request is not available outside of a handler call.")
        return self.__request

    def handle(self: "Handler", **kwargs: Any) -> Response:
        raise NotImplementedError("Handler must implement handle()")

    def __call__(self: "Handler", request: Request, **kwargs: Any) -> Response:
      self.__request = request # type: ignore
      try:
          return self.handle(**kwargs)
      except NotImplementedError:
          raise InternalServerException(
              detail=f"Handler '{type(self).__name__}' must implement the handle() method"
          )
