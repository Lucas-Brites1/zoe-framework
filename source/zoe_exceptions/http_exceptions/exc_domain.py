from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from abc import abstractmethod
from typing import Any

class DomainException(ZoeHttpException):
  def __init__(
      self,
      http_code: HttpCode,
      headers: dict[str, Any] | None = None):
    super().__init__(message="", status_code=http_code)
    self.headers = headers

  @abstractmethod
  def to_body(self, request: Request)  -> dict: ...

  def to_response(self, request: Request) -> Response:
    return Response.json(
      http_code=self.status_code,
      body=self.to_body(request=request),
      headers=self.headers
    )

  def __call__(self, request: Request) -> Response:
    return self.to_response(request=request)
