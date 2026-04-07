from typing import Any, Callable, TypeVar, overload

from zoe_exceptions.exc_internal_exc import InternalServerException, ZoeNonHttpError

T = TypeVar("T")
D = TypeVar("D")


class QueryParams:
    def __init__(self):
        self.__qparams: dict[str, list[str]] = {}

    def _set_param(self, key: str, value: str) -> None:
        if key in self.__qparams:
            self.__qparams[key].append(value)
            return

        self.__qparams[key] = [value]

    def _safe_cast(self, type_: Callable, value: str) -> Any:
        if type_ is bool:
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
            raise InternalServerException.from_non_http_error(
                ZoeNonHttpError(
                    why=f"Cannot cast '{value}' to bool",
                    explain=f"Value '{value}' is not a valid boolean string. bool() in Python does not parse strings — any non-empty string is True.",
                    fix="Use one of the accepted values: 'true', '1', 'yes' for True — 'false', '0', 'no' for False.",
                )
            )
        return type_(value)

    @overload
    def get(self, key: str, type_: Callable[[str], T], default: D) -> T | D: ...

    @overload
    def get(
        self, key: str, type_: Callable[[str], T], default: None = None
    ) -> T | None: ...

    @overload
    def get(self, key: str, type_: None = None, default: None = None) -> str | None: ...

    def get(
        self,
        key: str,
        type_: Callable[[str], T] | None = None,
        default: D | None = None,
    ) -> T | D | str | list | None:
        if key not in self.__qparams:
            return default

        values = self.__qparams[key]

        if type_ is not None:
            casted = []
            for v in values:
                try:
                    casted.append(self._safe_cast(type_=type_, value=v))
                except (ValueError, TypeError):
                    casted.append(default)
            return casted if len(casted) > 1 else casted[0]

        return values if len(values) > 1 else values[0]
