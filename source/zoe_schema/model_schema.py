from typing import Any

class Model:
  def __init__(self: "Model", **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)

  def __getattr__(self, name: str) -> Any:
    raise AttributeError(f"'{type(self).__name__}' has no field '{name}'")
