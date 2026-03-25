from zoe_net.protocols.base import ProtocolHandler, StreamReader, StreamWriter
from zoe_application.application import App
from zoe_http.request import Request
from zoe_http.response import Response

class HttpProtocol(ProtocolHandler):
    def __init__(self, application: App, request: Request) -> None:
        self.application = application
        self.request = request
    
    async def handle(self, reader: StreamReader, writer: StreamWriter) -> bool:
        response: Response = await self.application._resolve(self.request)
        writer.write(response._build())  
        await writer.drain()

        connection: str = self.request.headers.connection

        if self.request.http_version == "HTTP/1.1":
            return "close" not in connection
        
        return "keep-alive" in connection
