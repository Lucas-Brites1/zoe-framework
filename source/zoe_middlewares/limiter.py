from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_middlewares.limiter_client import LimiterClient
from typing import Callable, Any
from datetime import datetime
import threading

class Limiter(Middleware):
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
        self.__lock = threading.Lock()

    def __client_exists(self: "Limiter", ip: str) -> bool:
        return self.__clients.__contains__(ip)

    def __call__(self: "Limiter", request: Request, next: Callable) -> Response:
        with self.__lock:
          client: LimiterClient
          req_ip: str = request.client_ip

          if self.__client_exists(ip=req_ip):
              client = self.__clients[req_ip]
          else:
              self.__clients[req_ip] = LimiterClient(ip=req_ip)
              client = self.__clients[req_ip]

          elapsed_time: int = (datetime.now() - client.first_request_at).seconds

          if elapsed_time > self.__window_seconds:
              client.reset()

          client.increment()

          if client.request_count > self.__max_requests:
              return Response(http_status_code=HttpCode.TOO_MANY_REQUESTS)

          return next(request)
