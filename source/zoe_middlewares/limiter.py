from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_middlewares.limiter_client import LimiterClient
from typing import Callable, Any
from datetime import datetime
import threading

class Limiter(Middleware):
    def __init__(self: "Limiter", max_requests:int = 100, window_seconds:int = 60):
        self.__clients: dict[str, LimiterClient] = {}
        self.__max_requests = max_requests
        self.__window_seconds = window_seconds
        self.__lock = threading.Lock()

    def __client_exists(self: "Limiter", ip: str) -> bool:
        return self.__clients.__contains__(ip)

    def __call__(self: "Limiter", request: Request, next: Callable[[Request], Response]) -> Response:
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
