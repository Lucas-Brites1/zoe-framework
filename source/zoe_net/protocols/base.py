from zoe_http._request_util.request_headers import RequestHeaders
from abc import ABC, abstractmethod
from asyncio import StreamReader, StreamWriter
from enum import Enum

class Protocol(Enum):
    HTTP = "http"
    WEBSOCKET  = "websocket"

class ProtocolHandler(ABC):

    @abstractmethod
    async def handle(
        self,
        reader:  StreamReader,
        writer:  StreamWriter
        ) -> bool: 
        """
            Returns:
                bool: True if should keep connection alive
        """
        pass

    @staticmethod
    def detect(headers: RequestHeaders) -> Protocol:
        if (headers.get(key="upgrade", default="").lower() == "websocket" and "upgrade" in headers.get(key="connection", default="").lower()):
            return Protocol.WEBSOCKET
        
        return Protocol.HTTP

    @staticmethod
    def create(protocol: Protocol, **kwargs) -> "ProtocolHandler":
        from zoe_net.protocols.http_protocol import HttpProtocol

        match protocol:
            case Protocol.HTTP:
                return HttpProtocol(**kwargs)
            
            case Protocol.WEBSOCKET:
                ...

            case _:
                raise ValueError(f"Unsupported protocol: {protocol}")
    