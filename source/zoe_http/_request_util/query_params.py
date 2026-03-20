from typing import Any

class QueryParams:
    def __init__(self):
      self.__qparams: dict[str, list[str]] = {}

    def _set_param(self, key: str, value: str) -> None:
      if key in self.__qparams:
          self.__qparams[key].append(value)
          return

      self.__qparams[key] = [value]

    def __cast(self, value: str, t_cast: type, default_return: Any) -> Any:
      try:
         return t_cast(value)
      except (ValueError, TypeError):
         return default_return

    def get(self, key: str, type_: type = str, default: Any = None) -> list | Any | None:
        if key in self.__qparams:
            value: list[Any] | Any = self.__qparams[key]
            if len(value) > 1:
                if type_ != str:
                  return [self.__cast(v, type_, default) for v in value]
                return value
            else:
                if type_ != str:
                    return self.__cast(value=value[0], t_cast=type_, default_return=default)
                return value[0]
        return default

