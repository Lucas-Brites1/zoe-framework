from zoe_http.request import Request
from typing import Protocol

#'Bearer', 'Basic', 'ApiKey'
class GuardStrategy(Protocol):
    """
    Protocol (interface) that all Guard strategies must implement.
    ---
    If the built-in strategies don't fit your needs, you can create
    a custom one by implementing the `guard()` method in any class —
    no need to explicitly inherit from `GuardStrategy`.

    ---

    *Required method:*
    ```python
        def guard(self, request: Request) -> bool:
            ...
    ```
        *Returns* `True` to allow the request, `False` to block it with `401 Unauthorized`.
    ---

    *Example:*
    ```python
    from zoe import GuardStrategy, Request

    class IPWhitelistStrategy(GuardStrategy):
        def __init__(self, allowed_ips: list[str]) -> None:
            self.__allowed_ips = allowed_ips

        def guard(self, request: Request) -> bool:
            return request.client_ip in self.__allowed_ips
    ```
    """
    def guard(self: "GuardStrategy", request: Request) -> bool:
        raise NotImplementedError()

class BearerStrategy:
    def __init__(self: "BearerStrategy", token: str) -> None:
        self.__bearer_token: str = token

    def guard(self: "BearerStrategy", request: Request) -> bool:
        if request.auth.scheme != "Bearer":
            return False

        return request.auth.bearer_token == self.__bearer_token

class BasicStrategy:
    def __init__(self: "BasicStrategy", username: str, password: str) -> None:
      self.__username = username
      self.__password = password

    def guard(self: "BasicStrategy", request: Request) -> bool:
      credentials = request.auth.basic_credentials
      if not credentials:
          return False
      return credentials == (self.__username, self.__password)

class ApiKeyStrategy:
    def __init__(self: "ApiKeyStrategy", key: str):
        self.__key: str = key

    def guard(self: "ApiKeyStrategy", request: Request) -> bool:
        apikey: str = request.auth.api_key # type: ignore
        if not apikey:
            return False
        return apikey == self.__key

class AnyStrategy:
    def __init__(self: "AnyStrategy", strategies: list[GuardStrategy]) -> None:
        self.__strategies = strategies

    def guard(self: "AnyStrategy", request: Request) -> bool:
        for strategy in self.__strategies:
            if strategy.guard(request):
                return True
        return False

class AllStrategy:
    def __init__(self: "AllStrategy", strategies: list[GuardStrategy]) -> None:
        self.__strategies = strategies

    def guard(self: "AllStrategy", request: Request) -> bool:
        for strategy in self.__strategies:
            if not strategy.guard(request):
                return False
        return True
