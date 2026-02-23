from zoe_http.method import HttpMethod

class Route:
    def __init__(self: "Route", endpoint: str, method: HttpMethod) -> None:
        self.__endpoint = endpoint
        self.__method = method

    @property
    def endpoint(self: "Route") -> str:
        return self.__endpoint

    @property
    def method(self: "Route") -> HttpMethod:
        return self.__method


