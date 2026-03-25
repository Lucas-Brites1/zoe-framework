from zoe_net._server_util import _ServerUtil
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_application.application import App
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.http_exceptions.exc_heavy_payload import PayloadTooLargeException
from zoe_http.bytes import Bytes
from zoe_http._request_util.request_headers import RequestHeaders
from zoe_net.protocols.base import Protocol, ProtocolHandler
from zoe_net.protocols.http_protocol import HttpProtocol
import asyncio
import ssl

class Server:
    _CHUNK_SIZE: Bytes = Bytes.from_kb(n=5)
    _DEFAULT_MAX_REQUEST_SIZE: Bytes = Bytes.from_mb(n=10)
    _DEFAULT_KEEP_ALIVE_TIMEOUT_SECONDS: int = 30
    _LOCALHOST: str = "127.0.0.1"

    def __init__(
            self,
            application: App,
            host: str = "0.0.0.0",
            port: int = 8080,
            max_connections: int = 0,
            max_request_size: Bytes = _DEFAULT_MAX_REQUEST_SIZE,
            keep_alive_timeout: int = _DEFAULT_KEEP_ALIVE_TIMEOUT_SECONDS,
            ssl_certfile: str | None = None,
            ssl_keyfile: str | None = None,
            ssl_password: str | bytes | None = None,
            ssl_context: ssl.SSLContext | None = None
          ) -> None:
        self.__app = application

        self.__host = host
        self.__port = port
        self.__running = False

        self._max_connections = max_connections
        self._max_request_size = max_request_size
        self._keep_alive_timeout = keep_alive_timeout

        self.__tls_certificate: ssl.SSLContext | None = None

        if ssl_context:
            self.__tls_certificate = ssl_context

        elif ssl_certfile and ssl_keyfile:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(certfile=ssl_certfile, keyfile=ssl_keyfile, password=ssl_password)
            self.__tls_certificate = ctx

    async def __read_request(self, reader: asyncio.StreamReader) -> tuple[bytes, bytes] | None:
        raw: bytes = b""

        try:
            while b"\r\n\r\n" not in raw:
                chunk: bytes = await reader.read(self._CHUNK_SIZE.value)
                if not chunk:
                    return None
                raw += chunk

                if len(raw) > self._max_request_size.value:
                    raise PayloadTooLargeException()

            header_part, _, body_part = raw.partition(b"\r\n\r\n")

            content_length = 0
            for line in header_part.decode("utf-8", errors="replace").splitlines():
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":", 1)[1].strip())
                    break

            while len(body_part) < content_length:
                remaining = content_length - len(body_part)
                chunk = await reader.read(min(self._CHUNK_SIZE.value, remaining))
                if not chunk:
                    break
                body_part += chunk

            return (header_part, body_part)

        except asyncio.TimeoutError:
            return None

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while self.__running:
                try:
                    result = await self.__read_request(reader=reader)
                    if not result:
                        break
                except PayloadTooLargeException as exc:
                    response = exc.to_response()
                    writer.write(response._build())
                    await writer.drain()
                    break

                header_bytes, body_bytes = result

                if not header_bytes:
                    break


                req_headers = RequestHeaders(header_raw=header_bytes)
                protocol = ProtocolHandler.detect(headers=req_headers)
                
                client_ip, _ = writer.get_extra_info("peername")
                client_request = Request(
                    body_bytes=body_bytes,
                    client_ip=client_ip,
                    headers=req_headers
                )
                
                try:
                    should_continue = False
                    
                    if protocol == Protocol.HTTP:
                        handler = HttpProtocol(self.__app, client_request)
                        should_continue = await handler.handle(reader=reader, writer=writer)

                    # 5. Executar handler apropriado
                    elif protocol == Protocol.WEBSOCKET:
                        # Validar WebSocket
                        if not self._validate_websocket(headers):
                            await self._send_400(writer, "Invalid WebSocket handshake")
                            break
                        
                        # Enviar handshake 101
                        await self._send_websocket_handshake(writer, headers)
                        
                        # Criar handler e executar
                        #handler = WebSocketProtocol()
                        should_continue = await handler.handle(reader=reader, writer=writer)
                    
                    if not should_continue:
                        break
                
                except ZoeHttpException as exc:
                    # Enviar resposta de erro HTTP
                    response = exc.to_response()
                    writer.write(response._build())
                    await writer.drain()
                    break
                
                except Exception as exc:
                    # Erro interno
                    response = InternalServerException(detail=str(exc)).to_response()
                    writer.write(response._build())
                    await writer.drain()
                    break

        finally:
            writer.close()
            await writer.wait_closed()

    def run(self) -> None:
      try:
          asyncio.run(self._start())
      except KeyboardInterrupt:
          pass

    def _application_setup(self) -> None:
        self.__app._delete_merged_routers()
        self.__app.documentation

    async def _start(self) -> None:
      self.__running = True
      self._application_setup()

      server: asyncio.Server = await asyncio.start_server(
          client_connected_cb=self._handle,
          host=self.__host,
          port=self.__port,
          ssl=self.__tls_certificate
        )

      async with server:
          try:
            _ServerUtil.print_server_listening(host=self.__host, port=self.__port)
            self.__app._run_all_startup_callables()
            await server.serve_forever()
          except (KeyboardInterrupt, asyncio.CancelledError):
            pass
          finally:
            self.__running = False
            self.__app._run_all_shutdown_callables()
            _ServerUtil.print_server_shutdown()
