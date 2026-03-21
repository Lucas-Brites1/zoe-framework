from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from zoe_schema.field_schema_validator import FieldValidator
from typing import Any

class Required(FieldValidator):
    def validate(self, value: Any, field_name: str) -> None:
        if value is None:
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"Field '{field_name}' is required and cannot be null.",
                error_code=ErrorCode.VALUE_MISMATCH,
                details={
                    "received": None,
                    "expected": "A non-null value of any type",
                    "hint": f"Provide a valid value for '{field_name}' or mark it as optional"
                }
            )
