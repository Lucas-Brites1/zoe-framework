from zoe_net.protocols.base import ProtocolHandler, StreamReader, StreamWriter
from zoe_application.application import App
from zoe_http._request_util.request_headers import RequestHeaders
from zoe_http.request import Request
from zoe_http.response import Response
import hashlib
import base64

class WebsocketProtocol(ProtocolHandler):
    MAGIC_GUID_RFC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, headers: RequestHeaders) -> None:
        self._headers = headers
        self._handshake_done = False

    async def handle(self, reader: StreamReader, writer: StreamWriter) -> bool:
        if not self._handshake_done:
            await self.establish_handshake(writer=writer)
            self._handshake_done = True

        try:
            pass
            # Ler Frame
            # Processar Frame
        except Exception as exc:
            pass
        finally:
            writer.close()

        return False

    @property
    def handshake(self) -> bool:
        required_headers = {
            'upgrade': 'websocket',
            'connection': 'upgrade',
            'sec-websocket-version': '13'
        }

        for name, expected in required_headers.items():
            value: str = self._headers.get(key=name) or ""
            if value.lower() != expected:
                return False

        return 'sec-websocket-key' in self._headers

    async def establish_handshake(self, writer: StreamWriter) -> None:
        if not self.handshake:
            # faltam headers para aceitar conexao websocket
            raise ValueError # só template depois mudar para exceção específica do protoclo websocket que vou criar

        key: str | None = self._build_accept_key()
        if key is None:
            # websocket key inválida...
            raise ValueError # template, isso tem que levantar um erro

        response: bytes = self.switching_protocol_response(key)
        writer.write(response)
        await writer.drain()

    def _build_accept_key(self) -> str | None:
        key: str | None = self._headers.get('sec-websocket-key')
        if key is None:
            return None

        key += WebsocketProtocol.MAGIC_GUID_RFC

        bkey: bytes = key.encode(encoding="utf-8", errors="replace")
        SHA1_key: bytes =  hashlib.sha1(bkey).digest()
        response_b64: bytes = base64.b64encode(SHA1_key)
        response: str = response_b64.decode(encoding="utf-8", errors="replace")

        return response

    def switching_protocol_response(self, key: str) -> bytes:
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {key}\r\n"
            "\r\n"
        )
        return response.encode()
