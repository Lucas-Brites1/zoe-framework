from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.validation_exception import ValidatorException
from numbers import Real
from typing import Any

class Range(FieldValidator):
    def __init__(self, min: Real | None = None, max: Real | None = None):
        self.min = min
        self.max = max

    def __call__(self, value: Any, field_name: str) -> None:
        if self.min is not None and value < self.min:
            raise ValidatorException(field_name=field_name, message=f"'{field_name}' must be at least {self.min}")
        if self.max is not None and value > self.max:
            raise ValidatorException(field_name=field_name, message=f"'{field_name}' must be at most {self.max}")
