from typing import Any
class Body:
  def __init__(self: "Body", data: dict | str | bytes | None = None, content_type: str = "") -> None:
    self.__data: dict | str | bytes | None = data
    self.__type: str = content_type

  def get(self: "Body", key: str, default: Any | None = None) -> Any | None:
    if isinstance(self.__data, dict):
      return self.__data.get(key, default)
    return default

  @property
  def text(self: "Body") -> str | None:
    if isinstance(self.__data, str):
      return self.__data
    return None

  def is_json(self: "Body") -> bool:
    return "application/json" in self.__type

  @property
  def content_type(self: "Body") -> str | None:
    return self.__type

  @property
  def raw(self: "Body") -> bytes | None:
    if isinstance(self.__data, bytes):
      return self.__data
    return None

  @property
  def data(self: "Body") -> dict | str | bytes | None:
    return self.__data

  @classmethod
  def __parse_multipart(cls, body_bytes: bytes) -> dict:
    """
    b'
    ----------------------------c64d95cca9664deea325b3f6
    \r\nContent-Disposition: form-data; name="opa-key"; filename="texto-pequeno.txt"
    \r\nContent-Type: text/plain
    \r\n\r\ntextinho
    \r\n----------------------------c64d95cca9664deea325b3f6--
    \r\n'"""

    boundary_delimiter: list[bytes] = body_bytes.splitlines()
    print(boundary_delimiter)
    return {}

  @classmethod
  def __parse_body(cls, content_type: str, body_bytes: bytes) -> dict | str | bytes | None:
    result: dict | str | bytes | None = None
    base_type: str = content_type.split(";")[0].strip()

    match base_type:
      case "application/json":
        from json import loads, JSONDecodeError
        try:
          result = loads(body_bytes)
        except JSONDecodeError as e:
            raise JSONDecodeError(
                f"Failed to parse request body as JSON: {e.msg}",
                e.doc,
                e.pos
            ) from e

      case "text/plain" | "text/html" | "text/xml" | "application/xml":
        result = body_bytes.decode("utf-8")

      case "application/octet-stream":
        result = body_bytes

      case "multipart/form-data":
        result = cls.__parse_multipart(body_bytes)

      case "application/x-www-form-urlencoded":
        from urllib.parse import parse_qs
        result = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(body_bytes.decode()).items()}

      case _ if base_type.startswith(("image/", "audio/", "video/")):
        result = body_bytes

      case _:
        ... # Raise custom error invalid request content type? IDK no support for this type ?

    return result

  @classmethod
  def from_request(cls, content_type: str, body_bytes: bytes) -> "Body":
    if not body_bytes:
      return cls(None)

    data = cls.__parse_body(content_type, body_bytes)
    return cls(data, content_type)
