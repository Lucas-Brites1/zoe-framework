from typing import Any

class Model:
  def __init__(self: "Model", **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)

  def __getattr__(self: "Model", name: str) -> Any:
    raise AttributeError(f"'{type(self).__name__}' has no field '{name}'")

  def to_dict(self: "Model") -> dict:
    return self.__dict__

  @classmethod
  def is_model(cls, tipo) -> bool:
    for base in tipo.__mro__:
      if base.__name__ == "Model":
          return True
    return False

