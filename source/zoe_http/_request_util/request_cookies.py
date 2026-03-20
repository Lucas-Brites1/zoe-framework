class RequestCookie:
  def __init__(self):
    self.__cookies: dict[str, str] = {}

  def _parse_cookie_line(self, line: str):
    values: list[str] = line.split(sep=";")

    for val in values:
      if val is not None:
        key, value = val.split(sep="=", maxsplit=1)
        self.__cookies[key.strip()] = value.strip()

  def __iter__(self):
    return iter(self.__cookies.items())

