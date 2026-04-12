import types
import typing
from typing import Any

from zoe_di.inspector import FieldInfo, ModelInfo, ModelInspector
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException
from zoe_exceptions.schemas_exceptions.exc_base import ZoeSchemaException
from zoe_exceptions.schemas_exceptions.exc_type import ErrorCode
from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_schema.computed_field_schema import _ComputedField
from zoe_schema.field_schema import Field
from zoe_schema.model_schema import Model
from zoe_schema.schema_validators.not_null import NotNull
from zoe_schema.schema_validators.required import Required


class ModelEngine:
    __model_structure_cache: dict[str, tuple] = {}

    @staticmethod
    def validate_and_create(model_class: type[Model], data: dict) -> Model:
        cache_key = model_class.__name__

        if cache_key in ModelEngine.__model_structure_cache:
            model_info = ModelEngine.__get_cached_model_info(cache_key, data)
        else:
            model_info = ModelInspector._get_model_info(model_class, data)
            ModelEngine.__cache_model_structure(cache_key, model_info)

        strict_errors = ModelEngine.__validate_strict_mode(model_info, data)
        type_errors = ModelEngine.__validate_model_types(model_info, data)
        fields_with_type_errors = {e.field_name for e in type_errors}
        validator_errors = ModelEngine.__run_validators(
            model_info, fields_with_type_errors
        )

        errors = [*strict_errors, *type_errors, *validator_errors]
        if errors:
            raise ZoeSchemaAggregateException(errors=errors)

        return model_class(**ModelEngine.__processed_data(model_info=model_info))

    @staticmethod
    def __processed_data(model_info: ModelInfo) -> dict[str, Any]:
        processed_data_dict: dict[str, Any] = {}
        for field_name, field_info in model_info.model_fields.items():
            processed_data_dict[field_name] = field_info.field_body_value
        return processed_data_dict

    @staticmethod
    def __cache_model_structure(cache_key: str, model_info: ModelInfo) -> None:
        fields_structure = {}
        for field_name, field_info in model_info.model_fields.items():
            fields_structure[field_name] = {
                "iscomputed": isinstance(field_info.field_object, _ComputedField),
                "field_type": field_info.field_type,
                "field_is_optional": field_info.field_is_optional,
                "field_object": field_info.field_object,
            }
        ModelEngine.__model_structure_cache[cache_key] = (
            model_info.model_name,
            model_info.model_class,
            fields_structure,
        )

    @staticmethod
    def __get_cached_model_info(cache_key: str, data: dict) -> ModelInfo:
        model_name, model_class_cached, fields_structure = (
            ModelEngine.__model_structure_cache[cache_key]
        )

        tobe_processed: dict[str, _ComputedField] = {}
        fields = {}

        for field_name, field_meta in fields_structure.items():
            field_obj = field_meta["field_object"]
            iscomputed: bool = field_meta["iscomputed"]

            if iscomputed:
                tobe_processed[field_name] = field_obj
                continue

            field_value = ModelInspector._process_field_value(
                field=field_obj,
                field_name=field_name,
                field_type=field_meta["field_type"],
                data_ref=data,
            )

            fields[field_name] = FieldInfo(
                field_name=field_name,
                field_type=field_meta["field_type"],
                field_is_optional=field_meta["field_is_optional"],
                field_body_value=field_value,
                field_object=field_obj,
            )

        processed_values: dict[str, Any] = {
            name: info.field_body_value for name, info in fields.items()
        }

        for computed_field_name, computed_field_object in tobe_processed.items():
            lambda_value: Any = computed_field_object._lambda(processed_values)
            fields[computed_field_name] = FieldInfo(
                field_name=computed_field_name,
                field_body_value=lambda_value,
                field_is_optional=fields_structure[computed_field_name][
                    "field_is_optional"
                ],
                field_object=computed_field_object,
                field_type=fields_structure[computed_field_name]["field_type"],
            )

        return ModelInfo(
            model_name=model_name, model_class=model_class_cached, model_fields=fields
        )

    @staticmethod
    def __validate_strict_mode(
        model_info: ModelInfo, body_data: dict
    ) -> list[ZoeSchemaException]:
        is_strict = getattr(model_info.model_class, "_Model__strict__", False)

        if not is_strict:
            return []

        expected_fields = set(model_info.model_fields.keys())
        received_fields = set(body_data.keys())
        extra_fields = received_fields - expected_fields

        if extra_fields:
            return [
                ZoeSchemaException(
                    field_name=", ".join(sorted(extra_fields)),
                    message=(
                        f"Strict mode violation: Model '{model_info.model_name}' does not accept extra fields. "
                        f"Unexpected fields: {', '.join(sorted(extra_fields))}. "
                        f"Expected fields: {', '.join(sorted(expected_fields))}"
                    ),
                    error_code=ErrorCode.STRICT_MODE_VIOLATION,
                )
            ]

        return []

    @staticmethod
    def __resolve_list_of_models(
        field_name: str,
        value: list,
        item_type: type,
    ) -> tuple[list, list[ZoeSchemaException]]:
        """Resolve a list where items can be dicts or already-instantiated Model objects."""
        resolved = []
        errors = []

        for i, item in enumerate(value):
            if isinstance(item, item_type):
                resolved.append(item)
            elif isinstance(item, dict):
                try:
                    nested = ModelEngine.validate_and_create(
                        model_class=item_type, data=item
                    )
                    resolved.append(nested)
                except ZoeSchemaAggregateException as e:
                    errors.extend(e.errors)
            else:
                errors.append(
                    ZoeSchemaException(
                        field_name=field_name,
                        message=(
                            f"Field '{field_name}[{i}]' has invalid type. "
                            f"Expected '{item_type.__name__}' or dict, but received '{type(item).__name__}'."
                        ),
                        error_code=ErrorCode.TYPE_MISMATCH,
                    )
                )

        return resolved, errors

    @staticmethod
    def __validate_model_types(
        model_info: ModelInfo, data: dict
    ) -> list[ZoeSchemaException]:
        type_errors: list[ZoeSchemaException] = []

        for field_name, field_info in model_info.model_fields.items():
            value = field_info.field_body_value

            if value is None and not field_info.field_is_optional:
                came_in_body = field_name in data
                message = (
                    f"Field '{field_name}' cannot be null. Expected a value of type '{field_info.field_type}', but received null."
                    if came_in_body
                    else f"Field '{field_name}' is required but was not provided. Expected a value of type '{field_info.field_type}'."
                )
                type_errors.append(
                    ZoeSchemaException(
                        field_name=field_name,
                        message=message,
                        error_code=ErrorCode.VALUE_MISMATCH,
                    )
                )
                continue

            if value is None and field_info.field_is_optional:
                continue

            if value is not None and field_info.field_type is not None:
                expected_type = field_info.field_type
                actual_type = type(value)

                # nested Model from dict
                if (
                    isinstance(value, dict)
                    and isinstance(expected_type, type)
                    and Model.is_model(expected_type)
                ):
                    try:
                        nested_model = ModelEngine.validate_and_create(
                            model_class=expected_type, data=value
                        )
                        field_info.field_body_value = nested_model
                        continue
                    except ZoeSchemaAggregateException as e:
                        for error in e.errors:
                            error.field_name = f"{field_name}.{error.field_name}"
                        type_errors.extend(e.errors)
                        continue

                # already-instantiated nested Model
                if (
                    isinstance(value, Model)
                    and isinstance(expected_type, type)
                    and Model.is_model(expected_type)
                ):
                    if not isinstance(value, expected_type):
                        type_errors.append(
                            ZoeSchemaException(
                                field_name=field_name,
                                message=f"Field '{field_name}' has invalid type. Expected '{expected_type.__name__}', but received '{actual_type.__name__}'.",
                                error_code=ErrorCode.TYPE_MISMATCH,
                            )
                        )
                    continue

                origin = typing.get_origin(expected_type)

                # list[SomeModel] — items can be dicts OR already-instantiated models
                if origin is list:
                    args = typing.get_args(expected_type)
                    if args and isinstance(args[0], type) and Model.is_model(args[0]):
                        if not isinstance(value, list):
                            type_errors.append(
                                ZoeSchemaException(
                                    field_name=field_name,
                                    message=f"Field '{field_name}' has invalid type. Expected 'list', but received '{actual_type.__name__}'.",
                                    error_code=ErrorCode.TYPE_MISMATCH,
                                )
                            )
                            continue
                        resolved, errs = ModelEngine.__resolve_list_of_models(
                            field_name, value, args[0]
                        )
                        if errs:
                            type_errors.extend(errs)
                        else:
                            field_info.field_body_value = resolved
                        continue

                if origin in (typing.Union, types.UnionType):
                    args = typing.get_args(expected_type)

                    # unwrap Optional[list[SomeModel]]
                    for arg in args:
                        if arg is type(None):
                            continue
                        arg_origin = typing.get_origin(arg)
                        if arg_origin is list:
                            inner_args = typing.get_args(arg)
                            if (
                                inner_args
                                and isinstance(inner_args[0], type)
                                and Model.is_model(inner_args[0])
                            ):
                                if isinstance(value, list):
                                    resolved, errs = (
                                        ModelEngine.__resolve_list_of_models(
                                            field_name, value, inner_args[0]
                                        )
                                    )
                                    if errs:
                                        type_errors.extend(errs)
                                    else:
                                        field_info.field_body_value = resolved
                                    break
                    else:
                        valid_types = tuple(
                            typing.get_origin(t) or t
                            for t in args
                            if t is not type(None)
                        )
                        if not isinstance(value, valid_types):
                            type_names = " | ".join(
                                getattr(t, "__name__", str(t)) for t in valid_types
                            )
                            type_errors.append(
                                ZoeSchemaException(
                                    field_name=field_name,
                                    message=f"Field '{field_name}' has invalid type. Expected one of [{type_names}], but received '{actual_type.__name__}'.",
                                    error_code=ErrorCode.TYPE_MISMATCH,
                                )
                            )
                    continue

                check_type = typing.get_origin(expected_type) or expected_type
                if not isinstance(check_type, type):
                    continue
                if actual_type != check_type:
                    type_errors.append(
                        ZoeSchemaException(
                            field_name=field_name,
                            message=f"Field '{field_name}' has invalid type. Expected '{check_type.__name__}', but received '{actual_type.__name__}'.",
                            error_code=ErrorCode.TYPE_MISMATCH,
                        )
                    )

        return type_errors

    @staticmethod
    def __run_validators(
        model_info: ModelInfo, skip_fields: set[str] = set()
    ) -> list[ZoeSchemaException]:
        errors: list[ZoeSchemaException] = []
        skip_fields = skip_fields or set()

        for field_name, field_info in model_info.model_fields.items():
            if field_name in skip_fields:
                continue

            value = field_info.field_body_value
            if isinstance(field_info.field_object, _ComputedField):
                continue

            for validator in field_info.field_object.validators:
                if value is None and not isinstance(validator, (NotNull, Required)):
                    continue

                try:
                    validator.validate(value=value, field_name=field_name)
                except SchemaValidatorException as exc:
                    errors.append(exc)
                    break

        return errors
