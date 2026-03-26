class RequestCookie:
  def __init__(self):
    self.__cookies: dict[str, str] = {}

  def _parse_cookie_line(self, line: str):
    values: list[str] = line.split(sep=";")

    for val in values:
      if val is not None:
        key, value = val.split(sep="=", maxsplit=1)
        self.__cookies[key.strip()] = value.strip()

  def get(self, key: str) -> str | None:
    return self.__cookies[key] or None

  def __iter__(self):
    return iter(self.__cookies.items())

  def __contains__(self, key: str):
    return self.__cookies[key] is not None
