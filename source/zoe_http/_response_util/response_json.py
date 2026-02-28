from zoe_http.response import Response
from zoe_http.code import HttpCode

from typing import Any
import json

class Json(Response):
  _content_type = "application/json"
  def __init__(self: "Json", http_code: HttpCode, body: Any, headers: dict[str, Any] | None = None):
    super().__init__(http_code, headers)
    self._body = body

  def _build(self) -> bytes:
    response_message = self._status_line()

    body_data = None
    if self._body is not None:
      body_data = self.__serialize_to_json(self._body)
      body_json_str = json.dumps(body_data)

      response_message += self._content_line(content_type=self._content_type,body=body_json_str)
      response_message = self._apply_headers_to_response(response_str=response_message)

      if body_data is not None:
          response_message += body_json_str  # type: ignore

    return response_message.encode("utf-8")

  def __serialize_to_json(self, obj: Any) -> Any:
      if hasattr(obj, 'to_dict') and callable(obj.to_dict):
          return self.__serialize_to_json(obj=obj.to_dict())
      elif isinstance(obj, dict):
          return {k: self.__serialize_to_json(v) for k, v in obj.items()}
      elif isinstance(obj, list):
          return [self.__serialize_to_json(i) for i in obj]
      elif hasattr(obj, '__dict__') and not isinstance(obj, type):
          return self.__serialize_to_json(vars(obj))
      elif isinstance(obj, (str, int, float, bool)) or obj is None:
          return obj
      else:
          return str(obj)


