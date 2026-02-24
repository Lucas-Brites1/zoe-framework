from zoe_http.method import HttpMethod
from zoe_http.handler import Handler

class Route:
    def __init__(self: "Route", endpoint: str, method: HttpMethod, handler: Handler) -> None:
        self.__endpoint = endpoint
        self.__method = method
        self.__handler = handler

    @staticmethod
    def post(endpoint: str, handler: Handler) -> "Route":
        return Route(endpoint=endpoint, method=HttpMethod.POST, handler=handler)

    @staticmethod
    def get(endpoint: str, handler: Handler) -> "Route":
        return Route(endpoint=endpoint, method=HttpMethod.GET, handler=handler)

    @staticmethod
    def delete(endpoint: str, handler: Handler) -> "Route":
        return Route(endpoint=endpoint, method=HttpMethod.DELETE, handler=handler)

    @staticmethod
    def put(endpoint: str, handler: Handler) -> "Route":
        return Route(endpoint=endpoint, method=HttpMethod.PUT, handler=handler)

    @staticmethod
    def patch(endpoint: str, handler: Handler) -> "Route":
        return Route(endpoint=endpoint, method=HttpMethod.PATCH, handler=handler)

    @property
    def handler(self: "Route") -> Handler:
        return self.__handler

    @property
    def endpoint(self: "Route") -> str:
        return self.__endpoint

    @property
    def method(self: "Route") -> HttpMethod:
        return self.__method


