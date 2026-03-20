from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_http._response_util._pagination import Pagination, Filter
from typing import Any
import json

class Paginated(Response):
    def __init__(
        self, 
        items: list[Any], 
        pagination: Pagination,
        http_code: HttpCode = HttpCode.OK, 
        headers: dict[str, str] | None = None
    ) -> None: 
        super().__init__(http_code=http_code, headers=headers)

        self._items = items
        self._headers = headers or {}
        self._pagination: Pagination = pagination
    
    
    def _build(self) -> bytes:
        body = self._pagination._build()
        body_json = json.dumps(body, ensure_ascii=False)
        
        response = self._status_line()

        self.headers.add("Content-Type", "application/json; charset=utf-8")
        self.headers.add("Content-Length", str(len(body_json.encode("utf-8"))))
        
        response = self.headers._build(response)
        response += body_json
        
        return response.encode("utf-8")