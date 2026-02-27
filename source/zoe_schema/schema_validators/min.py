from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
import builtins

class Min:
    def __init__(self: "Min", min_: int) -> None:
        self.min = min_

    def validate(self: "Min", value: any, field_name: str) -> None:
        if value == None:
            return

        type_value: type = type(value)
        
        message_error: str | None = None
        details_error: dict | None = None
        #"'{field_name}' is too short. Minimum length is {self.min}, but got {length}."
        #details={"min_length": self.min, "received_length": length}
        
        match type_value:
            case builtins.str:
                length = len(value)
                if length < self.min:
                    message_error = f"'{field_name}' is too short. Minimum {self.min} characters, got {length}."
                    details_error = {"min": self.min, "received": length}

            case builtins.int | builtins.float:
                if value < self.min:
                    message_error = f"'{field_name}' is below the minimum value. Minimum is {self.min}, got {value}."
                    details_error = {"min": self.min, "received": value}

            case builtins.list | builtins.tuple:
                length = len(value)
                if length < self.min:
                    message_error = f"'{field_name}' has too few items. Minimum {self.min} items, got {length}."
                    details_error = {"min": self.min, "received": length}

            case _:
                pass

        if message_error or details_error:
            exc = SchemaValidatorException(
                field_name=field_name,
                message=message_error,
                error_code=ErrorCode.INVALID_LENGTH,
                details=details_error
            )
            raise exc
