import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_net.connection import Connection
from zoe_router.router import Router

LOCALHOST = "127.0.0.1"
class Server:
    def __init__(self: "Server", host: str = LOCALHOST, port: int = 8080, max_connections: int = 0) -> None:
            self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((host, port))
            self._max_connections = max_connections
            
            self.__router_container: list[Router] = []
    
    def add_router(self: "Server", router: Router) -> None:
        self.__router_container.append(router)

    def _handle(self: "Server", conn: "Connection") -> None:
        with conn.socket_connection:
            data = conn.retrieve_data_decoded()
            client_request: Request = Request(raw_data=data)
            # aqui a cadeia de middleware rodaria..
            # aqui eu leria todos os routers, veria se há a rota chamada e passaria a Request para a funcao handler da rota se ela existir
            # pegaria a Response e enviaria para o cliente a resposta

    def run(self) -> None:
        self._socket.settimeout(1.0) 
        self._socket.listen()
        pool = None

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