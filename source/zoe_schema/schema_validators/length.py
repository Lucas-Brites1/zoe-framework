from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from typing import Any

class Length:
    def __init__(self, min: int | None = None, max: int | None = None):
        self.min = min
        self.max = max

    def validate(self, value: Any, field_name: str) -> None:
        length = len(value)

        if self.min is not None and length < self.min:
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' is too short. Minimum length is {self.min}, but got {length}.",
                error_code=ErrorCode.INVALID_LENGTH,
                details={"min_length": self.min, "received_length": length}
            )

        if self.max is not None and length > self.max:
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' is too long. Maximum length is {self.max}, but got {length}.",
                error_code=ErrorCode.INVALID_LENGTH,
                details={"max_length": self.max, "received_length": length}
            )
