from zoe_exceptions.schemas_exceptions.exc_base import ZoeSchemaException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode

class SchemaTypeError(ZoeSchemaException):
    def __init__(self, field_name: str, expected: type, actual: type):
        super().__init__(
            field_name=field_name,
            message=(
                f"Field '{field_name}' expects type '{expected.__name__}', "
                f"but received '{actual.__name__}'."
            ),
            error_code=ErrorCode.TYPE_MISMATCH,
            details={
                "expected_type": expected.__name__,
                "received_type": actual.__name__
            }
        )


