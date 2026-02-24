from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.validation_exception import ValidatorException
from typing import Any

class Length:
    @staticmethod
    def _min(n: int) -> None:
       def validate(value: Any, field_name: str) -> None | ValidatorException:
            if len(value) < n:
                raise ValidatorException(field_name=field_name, message=f"'{field_name}' must have at least {n} characeters")
       return validate

    @staticmethod
    def _max(n: int) -> None:
        def validate(value: Any, field_name: str) -> None | ValidatorException:
            if len(value) > n:
                raise ValidatorException(field_name=field_name, message=f"'{field_name}' exceed the maximum number of characeters from {n}")
        return validate
