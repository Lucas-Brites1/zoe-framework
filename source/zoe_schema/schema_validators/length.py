from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.validation_exception import ValidatorException
from typing import Any
from numbers import Real

class Length(FieldValidator):
    def __init__(self: "Length", min: Real | None = None, max: Real | None = None):
        self.min = min
        self.max = max

    def __call__(self: "Length", value: Any, field_name: str) -> None:
        if self.min:
            if len(value) < self.min:
                raise ValidatorException(field_name=field_name, message=f"'{field_name}' must have at least {self.min} characeters")
        if self.max:
            if len(value) > self.max:
                raise ValidatorException(field_name=field_name, message=f"'{field_name}' exceed the maximum number of characeters from {self.max}")
