from typing import Any, Callable, TypeVar, overload

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
    def get(
        self, key: str, type_: Callable[[str], T], default: None = None
    ) -> T | None: ...

    @overload
    def get(self, key: str, type_: None = None, default: None = None) -> str | None: ...

    def _safe_cast(self, type_: Callable, value: str) -> Any:
        if type_ is bool:
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False

            from zoe_exceptions.exc_internal_exc import (
                InternalServerException,
                ZoeNonHttpError,
            )

            raise InternalServerException.from_non_http_error(
                ZoeNonHttpError(
                    why=f"Cannot cast '{value}' to bool",
                    explain=f"Value '{value}' is not a valid boolean string. bool() in Python does not parse strings — any non-empty string is True.",
                    fix="Use one of the accepted values: 'true', '1', 'yes' for True — 'false', '0', 'no' for False.",
                )
            )
        return type_(value)

    def get(
        self,
        key: str,
        type_: Callable[[str], T] | None = None,
        default: D | None = None,
    ) -> T | D | str | None:
        value = self.__params.get(key)
        if value is None:
            return default
        if type_ is not None:
            try:
                return self._safe_cast(type_=type_, value=value)
            except (ValueError, TypeError):
                return default
        return value
