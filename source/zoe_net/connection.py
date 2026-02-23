import socket

class Connection:
    @staticmethod
    def bootstrap(data: tuple) -> "Connection":
        return Connection(soc=data[0], addr=data[1])

    def __init__(self: "Connection", soc: socket.socket, addr: socket.AddressInfo):
        self.__sck_conn = soc
        self.__addr_conn = addr

    @property
    def socket_connection(self: "Connection") -> socket.socket:
        return self.__sck_conn

    @property
    def socket_address(self: "Connection") -> socket.AddressInfo:
        return self.__addr_conn

    def retrieve_data_encoded(self, buffer_size: int = 1024) -> bytes:
        chunks: list[bytes] = []
        while True:
            chunk = self.__sck_conn.recv(buffer_size)
            chunks.append(chunk)
            if len(chunk) < buffer_size:
                break
        return b"".join(chunks)

    def retrieve_data_decoded(self, buffer_size: int = 1024, decode_method: str = "utf-8") -> str:
        return self.retrieve_data_encoded(buffer_size).decode(decode_method)
