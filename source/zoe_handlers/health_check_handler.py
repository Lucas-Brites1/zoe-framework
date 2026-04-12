import time

from zoe_application.zoe_metadata import Zoe
from zoe_http.code import HttpCode
from zoe_http.handler import Handler
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_router.route import Route

_start_time: float = time.time()


class HealthCheck(Handler):
    @staticmethod
    def get_handler() -> Route:
        return Route.get(endpoint="/health", handler=HealthCheck())

    def handle(self: "HealthCheck", request: Request) -> Response:
        uptime_seconds: int = int(time.time() - _start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return Response.json(
            http_code=HttpCode.OK,
            body={
                "status": "healthy",
                "version": Zoe.version,
                "uptime": f"{hours}h {minutes}m {seconds}s",
                "framework": "Zoe",
            },
        )
