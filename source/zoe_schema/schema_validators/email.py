from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from zoe_exceptions.schemas_exceptions.exc_type import SchemaTypeError
from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
import re
from typing import Any

class Email:
    _PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def validate(self, value: Any, field_name: str) -> None:
        if not isinstance(value, str):
            raise SchemaTypeError(field_name, expected=str, actual=type(value))

        if not self._PATTERN.match(value):
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' must be a valid email address (e.g. user@domain.com). Got: '{value}'.",
                error_code=ErrorCode.INVALID_FORMAT,
                details={"received_value": value, "expected_format": "user@domain.com"}
            )
