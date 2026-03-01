import os
from pathlib import Path
from typing import Any

class Env:
  _loaded: bool = False
  _all_data: list = []

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
        cls._loaded = True
        return

    try:
        with open(env_file, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                cls._all_data.append({key: value})
                os.environ.setdefault(key.strip(), value.strip())
    except FileNotFoundError:
        pass

    cls._loaded = True

  @classmethod
  def get(cls, key: str, default: str | None = None) -> str | None:
      cls._load()
      return os.environ.get(key=key, default=default)

  @classmethod
  def required(cls, key: str) -> str | RuntimeError:
      cls._load()
      value = os.environ.get(key=key)
      if value is None:
          raise RuntimeError(f"Missing required environment variable: '{key}'")
      return value

  @classmethod
  def boolean(cls, key: str) -> bool:
      cls._load()
      value = cls.get(key)
      if value is None:
          return False
      return value.lower() in ("true", "1", "yes")

  @classmethod
  def integer(cls, key: str, default: int = 0) -> int | RuntimeError:
      cls._load()
      value = cls.get(key)
      if value is None:
        return default
      try:
          return int(value)
      except ValueError:
          raise RuntimeError(f"Environment variable '{key}' must be an integer, got '{value}'")

  @classmethod
  def list(cls, key: str, separator: str = ",", default: list | None = None) -> list[str]:
      cls._load()
      value = cls.get(key=key)
      if value is None:
        return default or []

      value = value.strip()
      if value.startswith("[") and value.endswith("]"):
          value = value[1:-1]

      return [item.strip() for item in value.split(separator)]
