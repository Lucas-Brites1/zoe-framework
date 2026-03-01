import socket

class Connection:
    @staticmethod
    def bootstrap(data: tuple) -> "Connection":
        return Connection(soc=data[0], addr=data[1])

    def __init__(self, soc: socket.socket, addr: socket.AddressInfo):
        self.__sck_conn = soc
        self.__addr_conn = addr

    @property
    def socket_connection(self) -> socket.socket:
        return self.__sck_conn

    @property
    def socket_address(self) -> socket.AddressInfo:
        return self.__addr_conn
