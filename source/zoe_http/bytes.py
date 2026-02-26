class Bytes:
    __kib = lambda n: n * 1024
    __mib = lambda n: n * 1024 * 1024
    __gib = lambda n: n * 1024 * 1024 * 1024

    def __init__(self: "Bytes", value: int) -> None:
        self.__value = value

    @property
    def value(self:"Bytes") -> int:
        return self.__value

    @staticmethod
    def from_kb(n: int) -> "Bytes":
        return Bytes(Bytes.__kib(n=n))

    @staticmethod
    def from_mb(n: int) -> "Bytes":
        return Bytes(Bytes.__mib(n=n))
    
    @staticmethod
    def from_gb(n: int) -> "Bytes":
        return Bytes(Bytes.__gib(n=n))