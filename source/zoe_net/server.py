import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from zoe_http.request import Request
from zoe_http.response import Response
from zoe_net.connection import Connection
from zoe_http.code import HttpCode
from zoe_application.application import Zoe


LOCALHOST = "127.0.0.1"
class Server:
    def __init__(self: "Server", application: Zoe, host: str = LOCALHOST, port: int = 8080, max_connections: int = 0) -> None:
            self.__app = application
            self.__host = host
            self.__port = port

            self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((host, port))
            self._max_connections = max_connections
            
    def _handle(self, conn: Connection) -> None:
        with conn.socket_connection:
            data = conn.retrieve_data_decoded()

            if not data.strip():
                return
                
            try:
                client_ip: str = conn.socket_address[0]    
                client_request: Request = Request(raw_data=data, client_ip=client_ip)
                response: Response = self.__app._resolve(request=client_request)
            except Exception as e:
                response = Response(http_status_code=HttpCode.BAD_REQUEST)
            
            conn.socket_connection.send(response._build())

    def run(self: "Server") -> None:
        self._socket.settimeout(1.0) 
        self._socket.listen()
        pool = None
        print(f"Server listening {self.__host}:{self.__port}")

        try:
            if self._max_connections > 0:
                pool = ThreadPoolExecutor(max_workers=self._max_connections)
                while True:
                    try:
                        conn = Connection.bootstrap(self._socket.accept())
                        pool.submit(self._handle, conn)
                    except socket.timeout:
                        continue 
            else:
                while True:
                    try:
                        conn = Connection.bootstrap(self._socket.accept())
                        thread = threading.Thread(target=self._handle, args=(conn,))
                        thread.daemon = True
                        thread.start()
                    except socket.timeout:
                        continue

        except KeyboardInterrupt:
            print("Shutting down server...")

        finally:
            if pool:
                pool.shutdown(wait=False)
            self._socket.close()