from typing import Any, overload, TypeVar, Callable, Type

T = TypeVar("T")
D = TypeVar("D")

class PathParams:
    def __init__(self):
        self.__params: dict[str, str] = {}

    def _set_param(self, key: str, value: str) -> None:
        self.__params[key] = value

    @overload
    def get(self, key: str, type_: Callable[[str], T], default: D) -> T | D: ...

    @overload
    def get(self, key: str, type_: Callable[[str], T], default: None = None) -> T | None: ...

    @overload
    def get(self, key: str, type_: None = None, default: None = None) -> str | None: ...

    def get(self, key: str, type_: Callable[[str], T] | None = None, default: D | None = None) -> T | D | str | None:
        value = self.__params.get(key)
        if value is None:
            return default
        if type_ is not None:
            try:
                return type_(value)
            except (ValueError, TypeError):
                return default
        return value
