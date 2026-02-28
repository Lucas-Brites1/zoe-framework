from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from zoe_application.zoe_metadata import ZoeMetadata
from typing import Any


class Assert:
  def __init__(self: "Assert", expected_value: str):
    self.expected_value = expected_value

  def validate(self: "Assert", value: Any, field_name: str) -> None:
    if type(value) == type(self.expected_value):
      if value == self.expected_value:
        return

    details: dict | None = None
    if ZoeMetadata.is_debug():
      details = {
        "expected_value": self.expected_value,
        "actual_value": value
      }

    raise SchemaValidatorException(
      field_name=field_name,
      error_code=ErrorCode.VALUE_MISMATCH,
      message="Assertion failed: The actual value does not equal the expected value.",
      details=details
    )
