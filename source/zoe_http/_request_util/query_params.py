from typing import Any, Callable, TypeVar, Type, overload

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

    @overload
    def get(self, key: str, type_: Callable[[str], T], default: D) -> T | D: ...

    @overload
    def get(self, key: str, type_: Callable[[str], T], default: None = None) -> T | None: ...

    @overload
    def get(self, key: str, type_: None = None,  default: None = None) -> str | None: ...

    def get(self, key: str, type_: Callable[[str], T] | None = None, default: D | None = None) -> T | D | str | list | None:
      if key not in self.__qparams:
          return default

      values = self.__qparams[key]

      if type_ is not None:
          casted = []
          for v in values:
              try:
                  casted.append(type_(v))
              except (ValueError, TypeError):
                  casted.append(default)
          return casted if len(casted) > 1 else casted[0]

      return values if len(values) > 1 else values[0]
