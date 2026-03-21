from zoe_exceptions.http_exceptions.exc_malformed_request import MalformedRequestException
from zoe_http._request_util.request_cookies import RequestCookie
from typing import TypeVar, Callable

T = TypeVar("T")

class RequestHeader:
    def __init__(self) -> None:
        self.__headers: dict[str, str] = {}
        self.__cookies: RequestCookie = RequestCookie()

    @property
    def values(self) -> dict[str, str]:
        return self.__headers

    @property
    def host(self) -> str:
        value = self.get("host")
        if value is None:
            raise MalformedRequestException("Missing Host header.")
        return value

    @property
    def content_type(self) -> str | None:
        return self.get("content-Type")

    @property
    def content_length(self) -> int | None:
        value = self.get("content-Length", type_=int)
        if not isinstance(value, int):
            return None
        return value

    # Optional
    @property
    def cookies(self) -> "RequestCookie":
        return self.__cookies

    @property
    def accept(self) -> str | None:
        return self.get("accept")

    @property
    def accept_encoding(self) -> str | None:
        return self.get("accept-encoding")

    @property
    def accept_language(self) -> str | None:
        return self.get("accept-language")

    @property
    def authorization(self) -> str | None:
        return self.get("authorization")

    @property
    def connection(self) -> str | None:
        return self.get("connection")

    @property
    def user_agent(self) -> str | None:
        return self.get("user-agent")

    @property
    def referer(self) -> str | None:
        return self.get("referer")

    @property
    def origin(self) -> str | None:
        return self.get("origin")

    @property
    def cache_control(self) -> str | None:
        return self.get("cache-control")

    @property
    def pragma(self) -> str | None:
        return self.get("pragma")

    @property
    def if_modified_since(self) -> str | None:
        return self.get("if-modified-since")

    @property
    def if_none_match(self) -> str | None:
        return self.get("if-none-match")

    @property
    def x_forwarded_for(self) -> str | None:
        return self.get("x-forwarded-for")

    @property
    def x_real_ip(self) -> str | None:
        return self.get("x-real-ip")

    @property
    def x_request_id(self) -> str | None:
        return self.get("x-request-id")

    def get(self, key: str, type_: Callable[[str], T] | None = None, default: T | None = None) -> T | str | None:
        value = self.__headers.get(key.lower())
        if value is None:
            return default
        if type_ is not None:
            try:
                return type_(value)
            except (ValueError, TypeError):
                return default
        return value

    def _parse(self, header_raw_part: list[str]) -> None:
        self.__headers = {}
        for header in header_raw_part:
            key, _, value = header.partition(": ")
            match key:
                case "Cookie":
                    self.__cookies._parse_cookie_line(line=value)
                case _:
                    self.__headers[key.lower()] = value
