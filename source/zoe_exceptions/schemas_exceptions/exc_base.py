from zoe_http.response import Response
from zoe_http.code import HttpCode
from enum import Enum

class ErrorCode(str, Enum):
    VALUE_MISMATCH         = "VALUE_MISMATCH"
    TYPE_MISMATCH          = "TYPE_MISMATCH"
    CONSTRAINT_VIOLATION   = "CONSTRAINT_VIOLATION"
    NULL_VALUE             = "NULL_VALUE"
    INVALID_FORMAT         = "INVALID_FORMAT"
    PATTERN_MISMATCH       = "PATTERN_MISMATCH"
    OUT_OF_RANGE           = "OUT_OF_RANGE"
    INVALID_LENGTH         = "INVALID_LENGTH"

class ZoeSchemaException(Exception):
    def __init__(
        self,
        field_name: str,
        message: str,
        error_code: ErrorCode,
        details: dict | None = None
    ):
        self.field_name = field_name
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

    def to_response(self, model_name: str) -> Response:
        return Response.json(
            http_code=HttpCode.BAD_REQUEST,
            body={
                "error": {
                    "type": "SCHEMA_VALIDATION_ERROR",
                    "code": self.error_code.value,
                    "model": model_name,
                    "field": self.field_name,
                    "message": self.message,
                    "details": self.details
                }
            }
        )
