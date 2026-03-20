from zoe_net._server_util import _ServerUtil
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_application.application import App
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.http_exceptions.exc_heavy_payload import PayloadTooLargeException
from zoe_http.bytes import Bytes
import asyncio

class Server:
    _CHUNK_SIZE: Bytes = Bytes.from_kb(n=5)
    _DEFAULT_MAX_REQUEST_SIZE: Bytes = Bytes.from_mb(n=10)
    _DEFAULT_KEEP_ALIVE_TIMEOUT_SECONDS: int = 30
    _LOCALHOST: str = "127.0.0.1"

    def __init__(
            self,
            application: App,
            host: str = _LOCALHOST,
            port: int = 8080,
            max_connections: int = 0,
            max_request_size: Bytes = _DEFAULT_MAX_REQUEST_SIZE,
            keep_alive_timeout: int = _DEFAULT_KEEP_ALIVE_TIMEOUT_SECONDS
          ) -> None:
        self.__app = application
        self.__host = host
        self.__port = port
        self._max_connections = max_connections
        self._max_request_size = max_request_size
        self._keep_alive_timeout = keep_alive_timeout
        self.__running = False

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

    def __should_keep_alive(self, header_bytes: bytes) -> bool:
        raw_data: str = header_bytes.decode("utf-8", errors="replace")

        for line in raw_data.splitlines():
            if line.lower().startswith("connection:"):
                return "keep-alive" in line.lower()
        if "HTTP/1.1" in raw_data.split("\r\n")[0]:
            return True
        return False

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
      try:
          while self.__running:
              try:
                result: tuple[bytes, bytes] | None = await self.__read_request(reader=reader)
              except PayloadTooLargeException as exc:
                  response = exc.to_response()
                  writer.write(response._build())
                  await writer.drain()
                  break

              if result is None:
                  break

              header_bytes, body_bytes = result

              if not header_bytes:
                  break

              client_ip, _ = writer.get_extra_info("peername")
              keep_alive = self.__should_keep_alive(header_bytes)

              try:
                  client_request = Request(
                      body_bytes=body_bytes,
                      header_bytes=header_bytes,
                      client_ip=client_ip
                  )
                  response = await self.__app._resolve(request=client_request)
              except ZoeHttpException as exc:
                  response = exc.to_response()
              except Exception as exc:
                  response = InternalServerException(detail=str(exc)).to_response()

              if keep_alive:
                  response.headers.add("Connection", "keep-alive")
                  response.headers.add("Keep-Alive", f"timeout={self._keep_alive_timeout}")
              else:
                  response.headers.add("Connection", "close")

              try:
                  writer.write(response._build())
                  await writer.drain()
              except Exception:
                  break

              if not keep_alive:
                  break

      finally:
          writer.close()
          await writer.wait_closed()

    def run(self) -> None:
      try:
          asyncio.run(self._start())
      except KeyboardInterrupt:
          pass

    async def _start(self) -> None:
      self.__running = True

      server: asyncio.Server = await asyncio.start_server(
          self._handle,
          self.__host, self.__port,
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
