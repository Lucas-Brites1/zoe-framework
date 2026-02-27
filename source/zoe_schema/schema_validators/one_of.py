from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from zoe_application.zoe_metadata import ZoeMetadata

class OneOf:
    def __init__(self: "OneOf", *options):
        self.options = options

    def validate(self: "OneOf", value: any, field_name: str) -> None:
        details: dict = {
            "received": value
        }
        if ZoeMetadata.is_debug():
            details["allowed"] = self.options
        
        exc: SchemaValidatorException = SchemaValidatorException(
                field_name=field_name,
                message=f"'{field_name}' must be one of the allowed values.",
                details=details,
                error_code=ErrorCode.CONSTRAINT_VIOLATION
            )

        if None not in self.options and value is None:
            raise exc
        if value not in self.options:
            raise exc