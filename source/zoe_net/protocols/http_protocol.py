from zoe_net.protocols.base import ProtocolHandler, StreamReader, StreamWriter
from zoe_application.application import App
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_di.container import Container
from time import perf_counter
from socket import gethostname

class HttpProtocol(ProtocolHandler):
    def __init__(self, application: App, request: Request) -> None:
        self.application = application
        self.request = request

    async def handle(self, reader: StreamReader, writer: StreamWriter) -> bool:
        Container._open_scope()
        try:
            response: Response = await self.application._resolve(self.request)
        finally:
            Container._close_scope()

        started_at: float = self.request.state.get("request_started_at") or perf_counter()
        elapsed_ms: float = (perf_counter() - started_at) * 1000

        response.add_header("X-Request-ID",    self.request.state.request_id)
        response.add_header("X-Response-Time", f"{elapsed_ms:.2f}ms")
        response.add_header("X-Powered-By",    "Zoe")
        response.add_header("X-Served-By",     gethostname())

        writer.write(response._build())
        await writer.drain()

        connection: str | None = self.request.headers.connection
        if connection is None:
            return False

        if self.request.http_version == "HTTP/1.1":
            return "close" not in connection

        return "keep-alive" in connection
