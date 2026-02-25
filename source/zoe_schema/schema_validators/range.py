from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from numbers import Real
from typing import Any

class Range(FieldValidator):
    def __init__(self, min: Real | None = None, max: Real | None = None):
        self.min = min
        self.max = max

    def validate(self, value: Any, field_name: str) -> None:
        if self.min is not None and value < self.min:
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' must be at least {self.min}. Got {value}.",
                error_code=ErrorCode.OUT_OF_RANGE,
                details={"min": self.min, "received_value": value}
            )

        if self.max is not None and value > self.max:
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' must be at most {self.max}. Got {value}.",
                error_code=ErrorCode.OUT_OF_RANGE,
                details={"max": self.max, "received_value": value}
            )