from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
import re
from typing import Any

class Pattern(FieldValidator):
    def __init__(self, regex: str) -> None:
        try:
            self.pattern = re.compile(regex)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern provided to Pattern validator: {e}")
        self.regex = regex

    def validate(self, value: Any, field_name: str) -> None:
        if not isinstance(value, (str, int, float)):
            raise SchemaValidatorException(field_name, expected=str, actual=type(value))

        string_value = str(value)
        if not self.pattern.match(string_value):
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' does not match the required format.",
                error_code=ErrorCode.PATTERN_MISMATCH,
                details={"pattern": self.regex, "received_value": string_value}
            )