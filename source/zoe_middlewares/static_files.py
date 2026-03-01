from zoe_http.response import Response
from zoe_http.request import Request
from zoe_exceptions.http_exceptions.exc_resource_not_found import NotFoundException
from zoe_http._file_util import FileUtil
from typing import Callable
from pathlib import Path

class StaticFiles:
  def __init__(self: "StaticFiles", directory: str | None = None, prefix_to_serv: str = "/static") -> None:
    self._prefix = prefix_to_serv
    self._dir = str(Path(directory).resolve()) if directory else None

  def _is_the_same_prefix(self: "StaticFiles", route: str) -> bool:
    if not self._prefix.startswith("/"):
      self._prefix = "/" + self._prefix

    return route.strip().startswith(self._prefix)

  def process(self, request: Request, next: Callable) -> Response:
    if self._is_the_same_prefix(route=request.route):
        filename = request.route.removeprefix(self._prefix).lstrip("/")

        if not filename:
            return NotFoundException("File").to_response()

        file_path = FileUtil.find(filename=filename, directory=self._dir)
        if file_path is None:
            return NotFoundException("File").to_response()

        return Response.file(filename=filename, directory=self._dir)

    return next(request)

