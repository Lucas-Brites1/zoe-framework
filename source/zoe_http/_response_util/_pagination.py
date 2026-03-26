from zoe_http.request import Request
from zoe_exceptions.http_exceptions.exc_malformed_request import MalformedRequestException
from dataclasses import dataclass
from typing import Any
from math import ceil

@dataclass
class Filter:
    name: str
    required: bool = True
    default: str | None = None

    def __post_init__(self):
        if self.required and self.default is not None:
            raise ValueError(
                f"Filter '{self.name}' cannot be both required and have a default value."
            )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "required": self.required,
            "default": self.default
        }

#MalformedRequestException
@dataclass
class Pagination:
    _PERPAGE_DEFAULT = 50
    _PERPAGE_MAX = 200

    items:   list[Any]
    request: Request
    total:   int
    perpage: int | None = None
    filters: list[Filter] | None = None
    first_page_url: str | None = None
    last_page_url:  str | None = None

    def __post_init__(self):
        if self.perpage is None:
            self.perpage = self.request.query_params.get(
                key="perpage",
                type_=int,
                default=self._PERPAGE_DEFAULT
            )

        if self.perpage > self._PERPAGE_MAX:
            self.perpage = self._PERPAGE_MAX

        if self.current_page is None:
            raise MalformedRequestException(
                detail="Query parameter 'page' is required for paginated responses"
            )

        if self.current_page > self.total_pages:
            raise MalformedRequestException(
                f"Page {self.current_page} does not exist. Maximum page is {self.total_pages}"
            )

        self.first_page_url = self._build_page_url(page=1)
        self.last_page_url  = self._build_page_url(self.total_pages)

    def _build_page_url(self, page: int) -> str:
        postfix: str = f"?page={page}&perpage={self.perpage}"

        filters_values: list[str] = self._get_filters_values()
        if filters_values:
            postfix += "&" + "&".join(filters_values)

        return self.request.route + postfix

    def _get_filters_values(self) -> list[str]:
        values: list[str] = []
        if self.filters is None:
            return values

        for f in self.filters:
            val: str | None = self.request.query_params.get(key=f.name)

            if val is None:
                if f.required:
                    raise MalformedRequestException(
                        detail=f"Required filter '{f.name}' is missing in query parameters"
                    )
                if f.default is None:
                    continue
                val = str(f.default)

            if isinstance(val, str):
                val = val.strip('"').strip("'")

            values.append(f"{f.name}={val}")

        return values

    def _get_applied_filters(self) -> list[dict]:
        if self.filters is None:
            return []
        return [f.to_dict() for f in self.filters]

    @property
    def _page_index(self) -> int:
        return self.current_page -1 if self.current_page is not None else 0

    @property
    def current_page(self) -> int | None:
        page = self.request.query_params.get(key="page", type_=int)
        if page is None:
            return None
        if page < 1:
            raise MalformedRequestException("Page must be >= 1")
        return page

    @property
    def prev_page(self) -> str | None:
        if self.current_page is None or self.current_page <= 1:
            return None
        return self._build_page_url(page=self.current_page - 1)

    @property
    def next_page(self) -> str | None:
        if self.current_page is None or self.total_pages is None:
            return None
        if self.current_page >= self.total_pages:
            return None

        return self._build_page_url(page=self.current_page + 1)

    @property
    def total_pages(self) -> int:
        if self.total is not None and self.perpage is not None and self.perpage > 0:
          return ceil(self.total / self.perpage)
        return 0

    @property
    def _iterrange(self) -> tuple[int, int]:
        if self._page_index is None or self.perpage is None:
            return (-1, -1)

        start: int = self._page_index * self.perpage
        end: int = min(start + self.perpage, self.total)
        return (start, end)

    def _build(self) -> dict:
        start, end = self._iterrange
        return {
            "data": self.items[start:end],
            "meta": {
                "total"         :     self.total,
                "total_pages"   :     self.total_pages,
                "current_page"  :     self.current_page,
                "per_page"      :     self.perpage,
                "start_index"   :     start,
                "end_index"     :     end
            },
            "links": {
                "prev"  :    self.prev_page,
                "next"  :    self.next_page,
                "first" :    self.first_page_url,
                "last"  :    self.last_page_url
            },
            "filters": self._get_applied_filters()
        }
