from zoe_http.middleware_async import AsyncMiddleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_middlewares.limiter_client import LimiterClient
from typing import Callable, Any
from datetime import datetime

class Limiter(AsyncMiddleware):
    def __init__(self, max_requests: int = 100, window_seconds: int = 60) -> None:
        """
        Rate limiting middleware based on client IP address.
        ---
        Tracks how many requests each client makes within a time window.
        If the limit is exceeded, the server responds with `429 Too Many Requests`.
        Recommended for all production environments to prevent brute force attacks.

        ---

        *Args:*
        - `max_requests` *(int)* — Maximum number of requests allowed per client
        within the time window. Defaults to `100`.
        - `window_seconds` *(int)* — Duration of the time window in seconds.
        Defaults to `60` *(1 minute)*.

        ---

        *Example:*
        ```python
            # 100 requests per minute (default)
            app.use(Limiter())

            # stricter — 20 requests per 30 seconds
            app.use(Limiter(max_requests=20, window_seconds=30))
        ```
        """
        self.__clients: dict[str, LimiterClient] = {}
        self.__max_requests = max_requests
        self.__window_seconds = window_seconds

    def __client_exists(self: "Limiter", ip: str) -> bool:
        return self.__clients.__contains__(ip)

    async def process_locked(self, request: Request, next: Callable) -> Response:
      req_ip = request.client_ip

      async with self.lock:
          if not self.__client_exists(ip=req_ip):
              self.__clients[req_ip] = LimiterClient(ip=req_ip)

          client = self.__clients[req_ip]
          elapsed_time = (datetime.now() - client.first_request_at).seconds

          if elapsed_time > self.__window_seconds:
              client.reset()

          client.increment()
          exceeded = client.request_count > self.__max_requests

      if exceeded:
          response = Response(http_code=HttpCode.TOO_MANY_REQUESTS)
          response.headers.add("Connection", "close")
          return response

      return await next(request)
