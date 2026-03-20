from enum import Enum
from typing import Any, NamedTuple

class SameSitePolicy(Enum):
    STRICT = "Strict"
    LAX    = "Lax"
    NONE   = "None"

class CookieAttributes:
    def __init__(self,
                 http_only:   bool = False,
                 secure:      bool = False,
                 partitioned: bool = False,
                 same_site:   SameSitePolicy | None = None,
                 max_age:     int | None = None,
                 expires:     str | None = None,
                 path:        str = "/",
                 domain:      str | None = None
                ):
        self.http_only   = "HttpOnly" if http_only else None
        self.secure      = "Secure" if secure else None
        self.partitioned = "Partitioned" if partitioned else None
        self.same_site   = f"SameSite={same_site.value}" if same_site else None
        self.max_age     = f"Max-Age={max_age}" if max_age is not None else None
        self.expires     = f"Expires={expires}" if expires else None
        self.domain      = f"Domain={domain}" if domain else None
        self.path        = f"Path={path}"

class CookiePair(NamedTuple):
  name: str
  value: str

class ResponseCookie:
  def __init__(self):
    self.__cokies: dict[str, str] = {}

  def add(self, pair: CookiePair, attributes: CookieAttributes | None = None) -> "ResponseCookie":
    cookie = f"{pair.name}={pair.value}"

    if attributes:
      parts = [
          attributes.path,
          attributes.max_age,
          attributes.expires,
          attributes.domain,
          attributes.same_site,
          attributes.http_only,
          attributes.secure,
          attributes.partitioned
      ]

      for part in parts:
         if part is not None:
            cookie += f"; {part}"

    self.__cokies[pair.name] = cookie
    return self

  def _build(self, to_append: str) -> str:
    for cookie in self.__cokies.values():
       to_append += f"Set-Cookie: {cookie}\r\n"

    return to_append
