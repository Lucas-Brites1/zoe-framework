from zoe_http.middleware import Middleware
from zoe_http.request import Request
from zoe_http.response import Response

from typing import Callable
from datetime import datetime

class Logger(Middleware):
    def __call__(self: "Logger", request: Request, next: Callable[[Request], Response]) -> Response:
        print(f"[{datetime.now()}] ({request.method.value}) {request.route}")
        return next(request)