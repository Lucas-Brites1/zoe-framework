from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from typing import Callable
from threading import Lock

class ThreadSafeMiddleware(Middleware):
  __lock: Lock
  def __new__(cls, *args, **kwargs):
    instance = super().__new__(cls)
    instance.__lock = Lock()
    return instance

  def process(self: "ThreadSafeMiddleware", request: Request, next: Callable) -> Response:
    with self.__lock:
      return self.process_locked(request, next)

  def process_locked(self, request: Request, next: Callable) -> Response:
      ...
