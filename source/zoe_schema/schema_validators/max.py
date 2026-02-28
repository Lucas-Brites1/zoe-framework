from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
import builtins
from typing import Any

class Max:
    def __init__(self: "Max", max_: int) -> None:
        self.max = max_

    def validate(self: "Max", value: Any, field_name: str) -> None:
        if value == None:
            return

        type_value: type = type(value)

        message_error: str | None = None
        details_error: dict | None = None
        #"'{field_name}' is too long. Maximum length is {self.max}, but got {value}."
        #details={"max_length": self.max, "received_length": length}

        match type_value:
            case builtins.str:
                length = len(value)
                if length > self.max:
                    message_error = f"'{field_name}' is too long. Maximum {self.max} characters, got {length}."
                    details_error = {"max": self.max, "received": length}

            case builtins.int | builtins.float:
                if value > self.max:
                    message_error = f"'{field_name}' exceeds maximum value. Maximum is {self.max}, got {value}."
                    details_error = {"max": self.max, "received": value}

            case builtins.list | builtins.tuple:
                length = len(value)
                if length > self.max:
                    message_error = f"'{field_name}' has too many items. Maximum {self.max} items, got {length}."
                    details_error = {"max": self.max, "received": length}

            case _:
                pass

        if message_error or details_error:
            exc = SchemaValidatorException(
                field_name=field_name,
                message=message_error, # type: ignore
                error_code=ErrorCode.INVALID_LENGTH,
                details=details_error
            )
            raise exc


