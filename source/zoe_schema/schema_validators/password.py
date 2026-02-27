from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from typing import Any

class Password:
  def __init__(
      self: "Password",
      min_length: int = 8,
      require_upper: bool = True,
      require_lower: bool = True,
      require_digits: bool = True,
      require_special: bool = True,
      special_chars: str = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
      ) -> None:
    self.__min_length = min_length
    self.__require_upper = require_upper
    self.__require_lower = require_lower
    self.__require_digits = require_digits
    self.__require_special = require_special
    self.__special_chars = special_chars

  def validate(self, value: Any, field_name: str) -> None:
        errors: list[str] = []

        if len(value) < self.__min_length:
            errors.append(f"at least {self.__min_length} characters")
        if self.__require_upper and not any(c.isupper() for c in value):
            errors.append("at least one uppercase letter")
        if self.__require_lower and not any(c.islower() for c in value):
            errors.append("at least one lowercase letter")
        if self.__require_digits and not any(c.isdigit() for c in value):
            errors.append("at least one digit")
        if self.__require_special and not any(c in self.__special_chars for c in value):
            errors.append(f"at least one special character ({self.__special_chars})")

        if errors:
            raise SchemaValidatorException(
                field_name=field_name,
                message=f"{field_name} must contain: {', '.join(errors)}.",
                error_code=ErrorCode.PATTERN_MISMATCH
            )

