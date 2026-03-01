import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from zoe_net._server_util import _ServerUtil
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_net.connection import Connection
from zoe_application.application import App
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException
from zoe_http.bytes import Bytes

class Server:
    _CHUNK_SIZE: Bytes = Bytes.from_kb(n=4)
    _DEFAULT_MAX_REQUEST_SIZE: Bytes = Bytes.from_mb(n=10)
    _DEFAULT_KEEP_ALIVE_TIMEOUT_SECONDS: int = 30

    def __init__(
            self,
            application: App,
            host: str = "127.0.0.1",
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
        self.__active_connections: list[socket.socket] = []
        self.__connections_lock = threading.Lock()

        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host, port))

    def __read_request(self, conn_socket: socket.socket) -> str | None:
        conn_socket.settimeout(self._keep_alive_timeout)
        raw: bytes = b""

        try:
            while b"\r\n\r\n" not in raw:
                chunk: bytes = conn_socket.recv(self._CHUNK_SIZE.value)
                if not chunk:
                    return None
                raw += chunk
                if len(raw) > self._max_request_size.value:
                    return None

            header_part, _, body_part = raw.partition(b"\r\n\r\n")

            content_length = 0
            for line in header_part.decode("utf-8", errors="replace").splitlines():
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":", 1)[1].strip())
                    break

            while len(body_part) < content_length:
                remaining = content_length - len(body_part)
                chunk: bytes = conn_socket.recv(min(self._CHUNK_SIZE.value, remaining))
                if not chunk:
                    break
                body_part += chunk

            return (header_part + b"\r\n\r\n" + body_part).decode("utf-8", errors="replace")

        except socket.timeout:
            return None
        except Exception:
            return None

    def __should_keep_alive(self, raw_data: str) -> bool:
        for line in raw_data.splitlines():
            if line.lower().startswith("connection:"):
                return "keep-alive" in line.lower()
        if "HTTP/1.1" in raw_data.split("\r\n")[0]:
            return True
        return False

    def __close_active_connections(self) -> None:
        with self.__connections_lock:
            for sock in self.__active_connections:
                try:
                    sock.close()
                except Exception:
                    pass
            self.__active_connections.clear()

    def _handle(self, conn: Connection) -> None:
        with self.__connections_lock:
            self.__active_connections.append(conn.socket_connection)

        try:
            with conn.socket_connection:
                while self.__running:
                    raw_data = self.__read_request(conn.socket_connection)

                    if not raw_data or not raw_data.strip():
                        break

                    client_ip: str = conn.socket_address[0]  # type: ignore
                    keep_alive = self.__should_keep_alive(raw_data)

                    try:
                        client_request = Request(raw_data=raw_data, client_ip=client_ip)
                        response = self.__app._resolve(request=client_request)
                    except ZoeHttpException as exc:
                        response = exc.to_response()
                    except Exception as exc:
                        response = InternalServerException(detail=str(exc)).to_response()

                    if keep_alive:
                        response.add_header("Connection", "keep-alive")
                        response.add_header("Keep-Alive", f"timeout={self._keep_alive_timeout}")
                    else:
                        response.add_header("Connection", "close")

                    try:
                        conn.socket_connection.sendall(response._build())
                    except Exception:
                        break

                    if not keep_alive:
                        break

        finally:
            with self.__connections_lock:
                try:
                    self.__active_connections.remove(conn.socket_connection)
                except ValueError:
                    pass

    def run(self) -> None:
        self.__running = True
        self._socket.settimeout(1.0)
        self._socket.listen(128)

        max_workers = self._max_connections if self._max_connections > 0 else None

        _ServerUtil.print_server_listening(host=self.__host, port=self.__port)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            try:
                while self.__running:
                    try:
                        conn = Connection.bootstrap(self._socket.accept())
                        pool.submit(self._handle, conn)
                    except socket.timeout:
                        continue
                    except OSError:
                        break

            except KeyboardInterrupt:
                self.__running = False
                self.__close_active_connections()
                _ServerUtil.print_server_shutdown()

            finally:
                pool.shutdown(wait=False, cancel_futures=True)
                self._socket.close()
