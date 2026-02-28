from zoe_exceptions.schemas_exceptions.exc_base import ZoeSchemaException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode

class SchemaValidatorException(ZoeSchemaException):
    def __init__(self, field_name: str, message: str, error_code: ErrorCode, details: dict | None = None):
        super().__init__(field_name, message, error_code, details)
