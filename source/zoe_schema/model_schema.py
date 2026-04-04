from typing import Any, Type
from typing import get_type_hints
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_internal_exc import InternalServerException

class Model:
  def __init_subclass__(cls, **kwargs):
    from zoe_di.inspector import ModelInspector
    super().__init_subclass__(**kwargs)
    ModelInspector._inspect_model(cls)

  def __init__(self: "Model", **kwargs):
    self._Model__strict: bool = getattr(self.__class__, '_Model__strict__', False)

    hints = get_type_hints(type(self))
    for field in hints:
      if field not in kwargs:
        setattr(self, field, None)
        continue
      setattr(self, field, kwargs[field])

  def __getattr__(self: "Model", name: str) -> Any:
    raise AttributeError(f"'{type(self).__name__}' has no field '{name}'")

  def __eq__(self: "Model", other: object) -> bool:
    if not isinstance(other, Model):
      return False
    return self.to_dict() == other.to_dict()

  def __hash__(self: "Model") -> int:
    try:
        return hash(frozenset(self.to_dict().items()))
    except TypeError:
        return hash(id(self))

  def clone(self, **overrides) -> "Model":
    data = self.to_dict()
    data.update(overrides)
    return self.__class__.create(**data)

  @classmethod
  def create(cls, **kwargs) -> "Model":
    from zoe_schema.model_engine import ModelEngine
    return ModelEngine.validate_and_create(cls, kwargs)

  @classmethod
  def from_dict(cls, data: dict) -> "Model":
      return cls.create(**data)

  @property
  def is_strict(self: "Model") -> bool:
    return self._Model__strict

  def to_dict(self: "Model") -> dict:
    result: dict = {}
    for attr_name, attr in self.__dict__.items():
      if attr_name.startswith("_"):
        continue
      result[attr_name] = self.__serialize(attr=attr)
    return result

  def __serialize(self, attr: Any) -> Any:
    if isinstance(attr, Model):
      return attr.to_dict()
    elif isinstance(attr, list):
      return [self.__serialize(item) for item in attr]
    else:
      return attr

  @property
  def example(self) -> dict[str, Any] | None: ...
  @property
  def examples(self) -> list[dict[str, Any]] | None: ...

  @classmethod
  def is_model(cls, class_reference: type) -> bool:
    return issubclass(class_reference, Model)

  def __str__(self: "Model") -> str:
    fields = "\n  ".join(
        f"{k}: {v}"
        for k, v in self.__dict__.items()
        if not k.startswith("_")
    )
    return f"{self.__class__.__name__}:\n  {fields}"

  def __repr__(self: "Model") -> str:
    fields = ", ".join(
        f"{k}={repr(v)}"
        for k, v in self.__dict__.items()
        if not k.startswith("_")
    )
    return f"{self.__class__.__name__}({fields})"

def Strict(cls: Type[Model]) -> Type[Model]:
  if not (isinstance(cls, type) and issubclass(cls, Model)):
    raise InternalServerException.from_non_http_error(error=ZoeNonHttpError(
      why="Invalid use of @Strict decorator",
      explain="Strict decorator can only be applied to model subclasses",
      fix=(
        f"Just use this decorator above any model subclass."
        f"@Strict"
        f"class User(Model):"
        f"\tname: str = Field(NotNull())..."
      ))
    )

  cls._Model__strict__ = True # type: ignore
  return cls

