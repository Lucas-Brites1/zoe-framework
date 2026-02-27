from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from typing import Any

class NotNull:
    def validate(self, value: Any, field_name: str) -> None:
        if value is None:
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' is required and cannot be null.",
                error_code=ErrorCode.NULL_VALUE
            )
