from datetime import datetime

class LimiterClient:
    def __init__(self: "LimiterClient", ip: str) -> None:
        self.__ip = ip
        self.__request_count: int = 0
        self.__first_request_at: datetime = datetime.now()

    @property
    def ip(self: "LimiterClient") -> str:
        return self.__ip
    
    @property
    def request_count(self: "LimiterClient") -> int:
        return self.__request_count

    @property
    def first_request_at(self: "LimiterClient") -> datetime:
        return self.__first_request_at

    def increment(self: "LimiterClient") -> None:
        self.__request_count += 1

    def reset(self: "LimiterClient") -> None:
        self.__request_count = 1
        self.__first_request_at = datetime.now()