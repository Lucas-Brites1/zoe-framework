from zoe_schema.model_schema import Model
from zoe_schema.field_schema import Field
from zoe_exceptions.schemas_exceptions.exc_base import ZoeSchemaException
from zoe_exceptions.schemas_exceptions.exc_type import SchemaTypeError
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException
from zoe_schema.schema_validators.not_null import NotNull
from zoe_schema.field_schema_validator import FieldValidator

from typing import Any
import typing
import types

class ModelEngine:
    @staticmethod
    def validate_and_create(model_class: type[Model], data: dict) -> Model:
        hints: dict = typing.get_type_hints(model_class)

        type_errors = ModelEngine.__validate_model_types(hints=hints, data=data)
        fields_with_type_errors = {e.field_name for e in type_errors}

        validator_errors = ModelEngine.__run_validators(
            class_dict=model_class.__dict__,
            data=data,
            skip_fields=fields_with_type_errors
        )

        errors = [*type_errors, *validator_errors]
        if errors:
            raise ZoeSchemaAggregateException(errors=errors)

        return model_class(**data)

    @staticmethod
    def __is_optional(hint: type) -> bool:
            origin = ModelEngine.__get_base_type(hint)
            if origin is typing.Union or origin == types.UnionType:
                args = typing.get_args(hint)
                return type(None) in args or type(types.UnionType) in args
            return False

    @staticmethod
    def __contains_multiple_internal_types(hint: type) -> bool:
            return typing.get_args(hint).__sizeof__() > 0


    @staticmethod
    def __get_base_type(hint: type) -> Any:
        origin = typing.get_origin(tp=hint)
        return origin if origin is not None else hint

    @staticmethod
    def __validate_model_types(hints: dict[str, type], data: dict) -> list[ZoeSchemaException]:
        type_errors: list[ZoeSchemaException] = []

        for field_name, expected_type in hints.items():
            if field_name == "return":
                continue
            if field_name not in data:
                continue

            actual_type = type(data[field_name])
            base_expected = ModelEngine.__get_base_type(hint=expected_type)

            if actual_type != base_expected:
                if ModelEngine.__is_optional(hint=typing.get_origin(expected_type)) and data[field_name] is None: # type: ignore
                    continue

                if ModelEngine.__contains_multiple_internal_types(hint=base_expected):
                    args: tuple = typing.get_args(tp=base_expected)
                    if expected_type in args:
                        continue

                type_errors.append(SchemaTypeError(
                    field_name=field_name,
                    expected=expected_type,
                    actual=actual_type
                ))

        return type_errors

    @staticmethod
    def __run_validators(
        class_dict: dict[str, type],
        data: dict,
        skip_fields: set[str] = set()
    ) -> list[ZoeSchemaException]:
        errors: list[ZoeSchemaException] = []
        skip_fields = skip_fields or set()

        for attr_name, attr_class in class_dict.items():
            if isinstance(attr_class, Field):
                if attr_name in skip_fields:
                    continue

                value = data.get(attr_name, None)

                for validator in attr_class.validators:
                    try:
                        if hasattr(validator, 'validate'):
                            if not isinstance(validator, NotNull) and value is None:
                                continue
                            validator.validate(value=value, field_name=attr_name)
                        else:
                            raise TypeError(
                                f"Validator '{type(validator).__name__}' on field '{attr_name}' "
                                f"must implement 'validate()' or be callable."
                            )
                    except ZoeSchemaException as exc:
                        errors.append(exc)
                        break

        return errors
