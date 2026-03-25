from zoe_http.response import Response
from zoe_http.code import HttpCode

class Empty(Response):
  def __init__(self) -> None:
    super().__init__(http_code=HttpCode.NO_CONTENT)
