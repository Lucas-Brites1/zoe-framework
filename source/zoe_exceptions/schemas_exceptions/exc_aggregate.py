from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_exceptions.schemas_exceptions.exc_base import ZoeSchemaException

class ZoeSchemaAggregateException(Exception):
    def __init__(self, errors: list[ZoeSchemaException]):
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s) occurred.")

    def to_response(self, model_name: str) -> Response:
        return Response(
            http_status_code=HttpCode.BAD_REQUEST,
            body={
                "error": {
                    "type": "SCHEMA_VALIDATION_ERROR",
                    "model": model_name,
                    "count": len(self.errors),
                    "errors": [
                        {
                            "code": e.error_code.value,
                            "field": e.field_name,
                            "message": e.message,
                            "details": e.details
                        }
                        for e in self.errors
                    ]
                }
            }
        )