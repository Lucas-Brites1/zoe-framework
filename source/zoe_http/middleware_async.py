from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from typing import Callable
import asyncio

class AsyncMiddleware(Middleware):
  _async_lock: asyncio.Lock | None = None

  @property
  def lock(self) -> asyncio.Lock:
    if self._async_lock is None:
      self._async_lock = asyncio.Lock()
    return self._async_lock

  async def process(self: "AsyncMiddleware", request: Request, next: Callable) -> Response:
      return await self.process_locked(request=request, next=next)

  async def process_locked(self, request: Request, next: Callable) -> Response:
      raise NotImplementedError
