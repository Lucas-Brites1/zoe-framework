import os
from pathlib import Path
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from typing import overload, TypeVar, Callable

T = TypeVar("T")
D = TypeVar("D")

class Env:
  _loaded: bool = False
  _strict_mode: bool = False

  @classmethod
  def strict(cls, enable: bool = True):
    cls._strict_mode = enable

  @classmethod
  def _find_env_file(cls) -> Path | None:
      current = Path.cwd()
      while True:
          candidate = current / ".env"
          if candidate.exists():
              return candidate
          parent = current.parent
          if parent == current:
              return None
          current = parent

  @classmethod
  def _load(cls) -> None:
    if cls._loaded:
        return

    env_file = cls._find_env_file()
    if env_file is None:
        if cls._strict_mode:
            raise ZoeNonHttpError(
            why="'.env' file not found",
            explain="Could not locate a '.env' file anywhere in the project directory tree.",
            fix=(
                "Create a '.env' file at the root of your project:\n\n"
                "  my_project/\n"
                "  ├── .env        ← here\n"
                "  ├── main.py\n"
                "  └── ...\n\n"
                "Example content:\n"
                "  DATABASE_URL=postgresql://user:password@localhost/db\n"
                "  SECRET_KEY=your-secret-key\n"
                "  DEBUG=true"
            )
        )
        cls._loaded = True
        return

    try:
        with open(env_file, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())
    except FileNotFoundError:
        pass

    cls._loaded = True

  @classmethod
  def required(cls, key: str, type_: type | None = None) -> str | RuntimeError:
    cls._load()

    value = os.environ.get(key=key)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: '{key}'")

    if type_ is not None:
          try:
              return type_(value)
          except (ValueError, TypeError):
              raise RuntimeError(f"Fail trying to convert '{value}' to '{type_.__name__}'")

    return value

  @classmethod
  @overload
  def get(cls, key: str, type_: Callable[[str], T], default: D) -> T | D: ...

  @classmethod
  @overload
  def get(cls, key: str, type_: Callable[[str], T], default: None = None) -> T | None: ...

  @classmethod
  @overload
  def get(cls, key: str, type_: None = None, default: None = None) -> str | None: ...

  @classmethod
  def get(cls, key: str, type_: Callable[[str], T] | None = None, default: D | None = None) -> T | D | str | None:
      cls._load()
      value = os.environ.get(key)
      if value is None:
          return default
      if type_ is not None:
          try:
              return type_(value)
          except (ValueError, TypeError):
              return default
      return value

  @classmethod
  @overload
  def list_of(cls, key: str, type_: Callable[[str], T], separator: str = ",", default: list[T] | None = None) -> list[T]: ...

  @classmethod
  @overload
  def list_of(cls, key: str, type_: None = None, separator: str = ",", default: list[str] | None = None) -> list[str]: ...

  @classmethod
  def list_of(cls, key: str, type_: Callable[[str], T] | None = None, separator: str = ",", default: list[T] | list[str] | None = None) -> list[str] | list[T]:
      cls._load()

      value = cls.get(key=key)
      if value is None:
          return default or []

      value = value.strip()
      if value.startswith("[") and value.endswith("]"):
          value = value[1:-1]

      items = [item.strip() for item in value.split(separator)]

      if type_ is not None:
          casted = []
          for item in items:
              try:
                  casted.append(type_(item))
              except (ValueError, TypeError):
                  pass
          return casted

      return items
