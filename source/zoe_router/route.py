from zoe_http.method import HttpMethod
from zoe_http.handler import Handler

class Route:
    def __init__(self: "Route", endpoint: str, method: HttpMethod, handler: Handler) -> None:
        self.__endpoint = endpoint
        self.__method = method
        self.__handler = handler

    @property
    def handler(self: "Route") -> Handler:
        return self.__handler

    @property
    def endpoint(self: "Route") -> str:
        return self.__endpoint

    @property
    def method(self: "Route") -> HttpMethod:
        return self.__method


