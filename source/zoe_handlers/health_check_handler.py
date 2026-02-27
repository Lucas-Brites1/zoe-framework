from zoe_http.handler import Handler
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_router.route import Route
from zoe_application.zoe_metadata import ZoeMetadata
import time

_start_time: time = time.time()

class HealthCheck(Handler):
    @staticmethod
    def get_handler() -> Route:
        return Route.get(endpoint="/health", handler=HealthCheck())

    def handle(self: "HealthCheck") -> Response:
        uptime_seconds: int = int(time.time() - _start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return Response(
                http_status_code=HttpCode.OK,
                body={
                "status": "healthy",
                "version": ZoeMetadata.version(),
                "uptime": f"{hours}h {minutes}m {seconds}s",
                "framework": ZoeMetadata.framework(),
                }
            )