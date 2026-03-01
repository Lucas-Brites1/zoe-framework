from zoe_http.response import Response
from zoe_http.code import HttpCode
import mimetypes
from zoe_http._file_util import FileUtil

class File(Response):
  __INLINE_TYPES = {
    "application/pdf",
    "image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml",
    "text/plain", "text/html",
    "video/mp4", "video/webm",
    "audio/mpeg", "audio/ogg",
  }

  def __init__(
          self,
          http_code: HttpCode,
          filename: str,
          directory: str | None = None,
          force_download: bool = False,
          headers: dict | None = None,
    ) -> None:
    super().__init__(http_code=http_code, headers=headers)
    self._content_type = mimetypes.guess_type(filename) or "application/octet-stream"
    self._dir = directory
    self._filename = filename
    self._force_download = force_download

  def __get_content_disposition(self) -> str:
     if self._content_type in self.__INLINE_TYPES and not self._force_download:
        return f"Content-Disposition: inline\r\n"
     return f'Content-Disposition: attachment; filename="{self._filename}"\r\n\r\n'

  def _build(self: "File") -> bytes:
    file_path = FileUtil.find(filename=self._filename, directory=self._dir)
    if file_path is None:
      raise FileNotFoundError

    file_bytes: bytes | None = FileUtil.read(path=file_path)
    if file_bytes is None:
      raise ValueError

    response_message: str = self._status_line()
    response_message += f"Content-Type: {self._content_type}\r\n"
    response_message += f"Content-Length: {len(file_bytes)}\r\n"
    response_message += self.__get_content_disposition()
    encoded_message: bytes = response_message.encode(encoding="utf-8")

    return encoded_message + file_bytes
