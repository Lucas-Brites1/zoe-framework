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
        value = self.get("Host")
        if value is None:
            raise MalformedRequestException("Missing Host header.")
        return value

    @property
    def content_type(self) -> str | None:
        return self.get("Content-Type")

    @property
    def content_length(self) -> int | None:
        value = self.get("Content-Length", type_=int)
        if not isinstance(value, int):
            return None
        return value

    # Optional
    @property
    def cookies(self) -> "RequestCookie":
        return self.__cookies

    @property
    def accept(self) -> str | None:
        return self.get("Accept")

    @property
    def accept_encoding(self) -> str | None:
        return self.get("Accept-Encoding")

    @property
    def accept_language(self) -> str | None:
        return self.get("Accept-Language")

    @property
    def authorization(self) -> str | None:
        return self.get("Authorization")

    @property
    def connection(self) -> str | None:
        return self.get("Connection")

    @property
    def user_agent(self) -> str | None:
        return self.get("User-Agent")

    @property
    def referer(self) -> str | None:
        return self.get("Referer")

    @property
    def origin(self) -> str | None:
        return self.get("Origin")

    @property
    def cache_control(self) -> str | None:
        return self.get("Cache-Control")

    @property
    def pragma(self) -> str | None:
        return self.get("Pragma")

    @property
    def if_modified_since(self) -> str | None:
        return self.get("If-Modified-Since")

    @property
    def if_none_match(self) -> str | None:
        return self.get("If-None-Match")

    @property
    def x_forwarded_for(self) -> str | None:
        return self.get("X-Forwarded-For")

    @property
    def x_real_ip(self) -> str | None:
        return self.get("X-Real-IP")

    @property
    def x_request_id(self) -> str | None:
        return self.get("X-Request-ID")

    def get(self, key: str, type_: Callable[[str], T] | None = None, default: T | None = None) -> T | str | None:
        value = self.__headers.get(key)
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
                    self.__headers[key] = value
