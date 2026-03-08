from zoe_http._request_util.upload_file import UploadFile
from typing import Any
class Multipart:
  def __init__(self, fields: dict[str, list[str]] , files: dict[str, list[UploadFile]]) -> None:
    self.__fields = fields
    self.__files = files

  #def file para UploadFile
  #def files para list[UploadFile] mesmo para field e fields
  def files(self, key: str) -> list[UploadFile] | None:
    if key in self.__files:
      founded: list[UploadFile] = self.__files[key]
      return founded
    return None

  def file(self, key: str) -> UploadFile | None:
    if key in self.__files:
      founded: list[UploadFile] = self.__files[key]
      return founded[0]
    return None

  def __cast_field(self, field: str, t_cast: type, default: Any) -> Any:
    try:
      return t_cast(field)
    except (ValueError, TypeError):
      return default

  def fields(self, key: str, type_: type = str, default: Any | None = None) -> list[Any] | None:
    if key in self.__fields:
      founded: list[str] = self.__fields[key]
      return [self.__cast_field(field=field, t_cast=type_, default=default) for field in founded]
    return default

  def field(self, key:str, type_: type = str, default: Any | None = None) -> Any | None:
    if key in self.__fields:
      founded: list[str] = self.__fields[key]
      return self.__cast_field(field=founded[0], t_cast=type_, default=default)
    return default

  @classmethod
  def empty(cls) -> "Multipart":
    return cls({}, {})

  @classmethod
  def __extract_header_value(cls, header_line: str, key: str) -> str | None:
    key_token = f"{key}="
    if key_token not in header_line:
        return None
    after = header_line.split(sep=key_token, maxsplit=1)[1]
    return after.split('"')[1]

  @classmethod
  def __parse_multipart(cls, content_type: str, body_bytes: bytes) -> tuple[dict[str, Any], dict[str, list[UploadFile]]]:
    fields: dict[str, list[str]] = {}
    files: dict[str, list[UploadFile]] = {}
    # content_type to extracts the boundary delimiter
    """
    b'
    ----------------------------c64d95cca9664deea325b3f6
    \r\nContent-Disposition: form-data; name="opa-key"; filename="texto-pequeno.txt"
    \r\nContent-Type: text/plain
    \r\n\r\ntextinho
    \r\n----------------------------c64d95cca9664deea325b3f6--
    \r\n'"""

    boundary_delimiter: str = content_type.split("=")[1]
    delimiter: bytes = b'--' + boundary_delimiter.encode(errors="replace")
    parts: list[bytes] = body_bytes.split(sep=delimiter)[1:-1]
    for p in parts:
      (header, content) = p.split(sep=b"\r\n\r\n", maxsplit=1)
      content = content.rstrip(b"\r\n")
      header_parts = header.decode().split("\r\n")[1:]
      is_file: bool = "filename" in header_parts[0]

      if is_file:
        key_name: str | None = None
        file_name: str | None = None
        file_type: str = ""

        for part in header_parts:
          if "Content-Type" in part:
            file_type = part.split(": ")[1]
          if "Content-Disposition" in part:
            key_name = cls.__extract_header_value(header_line=part, key="name")
            file_name = cls.__extract_header_value(header_line=part, key="filename")

        if key_name and file_name is not None:
          new_file = UploadFile(
            filename=file_name,
            type=file_type,
            data_bytes=content
          )

          if key_name in files:
            files[key_name].append(new_file)
          else:
            files[key_name] = [new_file]
      else:
        key_name: str | None = None

        for part in header_parts:
          key_name = cls.__extract_header_value(header_line=part, key="name")

        if key_name is not None:
          content_str = content.decode(encoding="utf-8", errors="replace")
          if key_name in fields:
            fields[key_name].append(content_str)
          else:
            fields[key_name] = [content_str]

    return (fields, files)

  @classmethod
  def from_request(cls, content_type: str, body_bytes: bytes) -> "Multipart":
    fields, files = cls.__parse_multipart(content_type=content_type, body_bytes=body_bytes)
    data = cls(fields, files)
    return data
