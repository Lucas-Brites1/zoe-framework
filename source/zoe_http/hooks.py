from inspect import isfunction
from typing import Callable, Any
from contextvars import ContextVar
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_http.request import Request

class Hook:

  class HookContext:
    __contexts: ContextVar[dict[str, Any] | None] = ContextVar("hook_context", default=None)

    def set(self, key: str, value: Any) -> None:
        ctx = self.__contexts.get({}) or {}
        self.__contexts.set({**ctx, key: value})

    def get(self, key: str) -> Any:
      ctx: dict = self.__contexts.get(None) or {}
      value: Any | None = ctx.get(key)
      if value is None:
          raise ZoeNonHttpError(
              why=f"Hook.ctx.get('{key}') failed",
              explain=f"'{key}' was never set in the current request context.",
              fix=(
                  f"Make sure you called Hook.ctx.set('{key}', value) "
                  f"inside your handler before the after hook runs:\n\n"
                  f"  def handle(self, request: Request) -> Response:\n"
                  f"      Hook.ctx.set('{key}', some_value)  ← here\n"
                  f"      return Response...."
              )
          )
      return value

    def try_get(self, key: str, default: Any | None = None):
       ctx: dict = self.__contexts.get({}) or {}
       value: Any | None = ctx.get(key)
       return default if value is None else value

    def _clear(self) -> None:
      self.__contexts.set(None)


  ctx: HookContext = HookContext()

  @classmethod
  def after(cls, call: Callable) -> "Hook":
     return cls(call)

  def __init__(self, call: Callable) -> None:
    self.after_fn = call

  def __call__(self, handler):
        from zoe_http._handler_util.handler_invoker import HandlerInvoker, Handler

        if isfunction(handler):
          handler.__afterfn__ = self.after_fn             # type: ignore
          return handler

        elif isinstance(handler, type) and issubclass(handler, Handler):
          handler.__original_handle__ = handler.handle    # type: ignore
          handler.__afterfn__ = self.after_fn             # type: ignore

          async def wrapped_handle(self_handler, **kwargs):
              request_from_handler: Request | None = self.__retrieve_request_from_handler_class(kwargs)
              if request_from_handler is None:
                raise

              response = await HandlerInvoker.invoke(self_handler, request_from_handler)
              return response

          handler.handle = wrapped_handle                 # type: ignore
          return handler

        else:
            raise ZoeNonHttpError(
              why=f"@After applied to invalid type '{type(handler).__name__}'",
              explain="@After can only be applied to Handler subclasses or functions.",
              fix=(
                  "@After(fn)\n"
                  "class MyHandler(Handler): ...\n\n"
                  "or:\n\n"
                  "@After(fn)\n"
                  "def my_handler(req: Request) -> Response: ..."
              )
          )

  def __retrieve_request_from_handler_class(self, kwargs: dict) -> Request | None:
    for value in kwargs.values():
        if isinstance(value, Request):
            return value
    return None
