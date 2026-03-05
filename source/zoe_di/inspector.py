from inspect import Signature, signature, Parameter, isfunction, isclass
from typing import get_type_hints, Type, Any, Callable
from dataclasses import dataclass
from enum import Enum

class ObjectKind(Enum):
  INSTANCE = "instance" # Provided
  CLASS = "class"       # Singleton, Scoped, Transient
  FUNC = "function"     # Singleton, Scoped, Transient
  PRIMITIVE = "primitive"

  @classmethod
  def from_object(cls, object: Any) -> "ObjectKind":
      if isfunction(object=object):
          return cls.FUNC
      elif isclass(object=object):
          return cls.CLASS
      elif isinstance(object, (str, int, float, bool, list, dict, tuple)):
        return cls.PRIMITIVE
      else:
          return cls.INSTANCE

@dataclass
class ParamInfo:
  param_type: Type | None
  param_is_required: bool
  param_default_value: Any

@dataclass
class CallableInfo:
  callable_name: str
  callable_ref: Callable
  callable_params: dict[str, ParamInfo]
  callable_return_type: Type | None

class Inspector:
  @staticmethod
  def callable_infos(fn: Callable, skip_self: bool = True) -> CallableInfo:
    params: dict[str, ParamInfo] = {}
    fn_sig: Signature = signature(obj=fn)
    fn_hints: dict = get_type_hints(obj=fn)

    for param_name, param in fn_sig.parameters.items():
      if skip_self and param_name == 'self':
        continue

      is_required: bool = param.default is Parameter.empty
      default_value: Any = None if param.default is Parameter.empty else param.default

      params[param_name] = ParamInfo(
        param_type=fn_hints.get(param_name, None),
        param_is_required=is_required,
        param_default_value=default_value
      )

    return CallableInfo(
      callable_name=fn.__name__,
      callable_ref=fn,
      callable_params=params,
      callable_return_type=fn_hints.get("return")
    )

  @staticmethod
  def object_kind(obj: Any) -> ObjectKind:
    return ObjectKind.from_object(object=obj)
