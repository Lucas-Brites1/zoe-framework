from typing import Any

class PathParams:
    def __init__(self):
        self.__pparms: dict[str, list[str]] = {}

    def _set_param(self, key: str, value: str) -> None:
      if key in self.__pparms:
          self.__pparms[key].append(value)
          return

      self.__pparms[key] = [value]

    def __cast(self, value: str, t_cast: type, default: Any) -> Any:
        try:
            return t_cast(value)
        except (ValueError, TypeError):
            return default

    def get(self, key: str, type_: type = str, default: Any | None = None) -> Any | None:
      if key in self.__pparms:
        value: list[Any] | Any = self.__pparms[key]
        if len(value) > 1:
          if type_ != str:
            return [self.__cast(v, type_, default) for v in value]
          return value
        else:
          if type_ != str:
            return self.__cast(value=value[0], t_cast=type_, default=default)
          return value[0]
      return None
