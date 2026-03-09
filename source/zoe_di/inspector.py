from inspect import Signature, signature, Parameter, isfunction, isclass
from typing import get_type_hints, Type, Any, Callable, get_origin, get_args, Union
from types import UnionType
from dataclasses import dataclass
from enum import Enum
from zoe_schema.model_schema import Model
from zoe_schema.field_schema import Field, FieldValidator
from zoe_schema.schema_validators.not_null import NotNull
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError

from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_internal_exc import InternalServerException
import typing
import types

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

@dataclass
class FieldInfo:
  field_name: str
  field_type: Type | None
  field_is_optional: bool
  field_body_value: Any
  field_object: Field

@dataclass
class ModelInfo:
  model_name: str
  model_class: Type[Model]
  model_fields: dict[str, FieldInfo]

class ModelInspector:
  #is_optional@ #_process_field_value@ #_get_fields@ # get_model_info #validate_strict_mode
  @staticmethod
  def _get_fields(model_ref: Type[Model], data_ref: dict[str, Any]) -> dict[str, FieldInfo]:
    fields_: dict[str, FieldInfo] = {}
    hints: dict[str, Type] = get_type_hints(model_ref)
    model_dict: dict[str, Any] = model_ref.__dict__

    for attr_name, attr_type in hints.items():
        if attr_name == "return" or attr_name.startswith("_"):
            continue

        field_obj: Field | None = model_dict.get(attr_name)

        if not isinstance(field_obj, Field):
            field_obj = Field()

        if field_obj.default_value is not None:
            ModelInspector._validate_default_type(
                field_name=attr_name,
                field_type=attr_type,
                default_value=field_obj.default_value,
                model_name=model_ref.__name__
            )
        
        field_value: Any = ModelInspector._process_field_value(
            field=field_obj, 
            field_type=attr_type,
            field_name=attr_name, 
            data_ref=data_ref
        )
        
        fields_[attr_name] = FieldInfo(
            field_name=attr_name,
            field_type=attr_type,
            field_is_optional=ModelInspector.is_optional(type_hint=attr_type),
            field_body_value=field_value,
            field_object=field_obj
        )

    return fields_

  @staticmethod
  def _validate_default_type(
      field_name: str, 
      field_type: Type, 
      default_value: Any,
      model_name: str
  ) -> None:
      
      default_type = type(default_value)
      
      if default_type is bool:
          origin = typing.get_origin(field_type)
          
          if origin in (typing.Union, types.UnionType):
              valid_types = tuple(t for t in typing.get_args(field_type) if t is not type(None))
              if bool not in valid_types:
                  valid_names = " | ".join(t.__name__ for t in valid_types)
                  raise InternalServerException.from_non_http_error(
                      error=ZoeNonHttpError(
                          why=f"Invalid default value type for field '{field_name}' in model '{model_name}'",
                          explain=(
                              f"Field '{field_name}' expects type [{valid_names}], "
                              f"but default value is 'bool'. "
                              f"Note: bool is not accepted as int in strict type checking."
                          ),
                          fix=(
                              f"Change the default value to match one of the expected types:\n"
                              f"  {field_name}: {valid_names} = Field(default=<valid_value>)\n"
                              f"Or add 'bool' to the type hint:\n"
                              f"  {field_name}: {valid_names} | bool = Field(default={default_value})"
                          )
                      )
                  )
          elif field_type is not bool:
              raise InternalServerException.from_non_http_error(
                  error=ZoeNonHttpError(
                      why=f"Invalid default value type for field '{field_name}' in model '{model_name}'",
                      explain=(
                          f"Field '{field_name}' expects type '{field_type.__name__}', "
                          f"but default value is 'bool'."
                      ),
                      fix=(
                          f"Change the default value to match the expected type:\n"
                          f"  {field_name}: {field_type.__name__} = Field(default=<valid_value>)\n"
                          f"Or change the type hint to 'bool':\n"
                          f"  {field_name}: bool = Field(default={default_value})"
                      )
                  )
              )
          return 
      
      origin = typing.get_origin(field_type)
      if origin in (typing.Union, types.UnionType):
          valid_types = tuple(t for t in typing.get_args(field_type) if t is not type(None))
          
          if default_type not in valid_types:
              valid_names = " | ".join(t.__name__ for t in valid_types)
              raise InternalServerException.from_non_http_error(
                  error=ZoeNonHttpError(
                      why=f"Invalid default value type for field '{field_name}' in model '{model_name}'",
                      explain=(
                          f"Field '{field_name}' expects type [{valid_names}], "
                          f"but default value has type '{default_type.__name__}'"
                      ),
                      fix=(
                          f"Change the default value to match one of the expected types:\n"
                          f"  {field_name}: {valid_names} = Field(default=<valid_value>)"
                      )
                  )
              )
      else:
          if default_type != field_type:
              raise InternalServerException.from_non_http_error(
                  error=ZoeNonHttpError(
                      why=f"Invalid default value type for field '{field_name}' in model '{model_name}'",
                      explain=(
                          f"Field '{field_name}' expects type '{field_type.__name__}', "
                          f"but default value has type '{default_type.__name__}'"
                      ),
                      fix=(
                          f"Change the default value to match the expected type:\n"
                          f"  {field_name}: {field_type.__name__} = Field(default=<valid_value>)"
                      )
                  )
              )

  @staticmethod
  def is_optional(type_hint: Type) -> bool:
    origin = get_origin(type_hint)
    if origin in (Union, UnionType):
        return type(None) in get_args(type_hint)
    return False

  @staticmethod
  def _process_field_value(field: Field, field_name: str, field_type: Type, data_ref: dict[str, Any]) -> Any:
      if field_name in data_ref:
          return data_ref[field_name]

      if field.is_required:
          raise InternalServerException.from_non_http_error(
              error=ZoeNonHttpError(
                  why="Missing required field",
                  explain=(
                      f"The field '{field_name}' is required but was not provided. "
                      f"Expected type: {field_type}"
                  ),
                  fix=f"Add '{field_name}' to your input data with a valid {field_type} value"
              )
          )

      return field.default_value if field.default_value is not None else None

  @staticmethod
  def _get_model_info(model_ref: Type[Model], body_data: dict[str, Any]) -> ModelInfo:
    return ModelInfo(
      model_name=model_ref.__name__,
      model_class=model_ref,
      model_fields=ModelInspector._get_fields(model_ref=model_ref, data_ref=body_data)
    ) 

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
