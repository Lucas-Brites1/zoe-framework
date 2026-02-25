from zoe_schema.field_schema import Field
from zoe_exceptions.schemas_exceptions.schema_unexpected_type import SchemaFieldUnexpectedType

from typing import Any, Type
import typing

class Model:
  def __init__(self: "Model", **kwargs):
    hints = typing.get_type_hints(type(self))

    for field_name, expected_type in hints.items():
      if field_name in kwargs:
        value = kwargs[field_name]
        type_of_value = type(value)
        if expected_type != type_of_value:
          raise SchemaFieldUnexpectedType(field_name=field_name, field_expected_type=expected_type, field_actual_type=type_of_value)

    for field_name, field_def in self.__class__.__dict__.items():
      if isinstance(field_def, Field):
        value = kwargs.get(field_name, None)
        for validator in field_def.validators:
            validator.__call__(value=value, field_name=field_name)

    for key, value in kwargs.items():
      setattr(self, key, value)
      print(f"key: {key} | value: {value}")


  def __getattr__(self: "Model", name: str) -> Any:
    raise AttributeError(f"'{type(self).__name__}' has no field '{name}'")

  def to_dict(self: "Model") -> dict:
    return self.__dict__

  @classmethod
  def is_model(cls, class_reference: type) -> bool:
    for base in class_reference.__mro__:
      if base.__name__ == "Model":
          return True
    return False

