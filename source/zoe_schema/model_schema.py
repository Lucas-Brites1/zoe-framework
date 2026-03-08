from typing import Any
from typing import get_type_hints

class Model:
  def __init__(self: "Model", **kwargs):
    hints = get_type_hints(type(self))
    for field in hints:
      if field not in kwargs:
        setattr(self, field, None)
        continue
      setattr(self, field, kwargs[field])

  def __getattr__(self: "Model", name: str) -> Any:
    raise AttributeError(f"'{type(self).__name__}' has no field '{name}'")

  def to_dict(self: "Model") -> dict:
    result: dict = {}
    for attr_name, attr in self.__dict__.items():
      result[attr_name] = self.__serialize(attr=attr)
    return result

  def __serialize(self, attr: Any) -> Any:
    if isinstance(attr, Model):
      return attr.to_dict()
    elif isinstance(attr, list):
      return [self.__serialize(item) for item in attr]
    else:
      return attr

  @classmethod
  def is_model(cls, class_reference: type) -> bool:
    return issubclass(class_reference, Model)

