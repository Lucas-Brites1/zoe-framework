from zoe_exceptions.schemas_exceptions.exc_base import ZoeSchemaException
from zoe_http.code import HttpCode
from zoe_http.response import Response


class ZoeSchemaAggregateException(Exception):
    def __init__(self, errors: list[ZoeSchemaException]):
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s) occurred.")

    def to_response(
        self, model_name: str | None = None, detailed: bool = True
    ) -> Response:
        if detailed:
            return Response.json(
                http_code=HttpCode.BAD_REQUEST,
                body={
                    "error": {
                        "type": "SCHEMA_VALIDATION_ERROR",
                        "model": model_name or "undefined",
                        "message": f"Validation failed for {len(self.errors)} field(s)",
                        "count": len(self.errors),
                        "errors": [
                            {
                                "code": e.error_code.value,
                                "field": e.field_name,
                                "message": e.message,
                                "details": e.details,
                            }
                            for e in self.errors
                        ],
                    }
                },
            )
        return Response.json(
            http_code=HttpCode.BAD_REQUEST,
            body={
                "error": {
                    "type": "VALIDATION_ERROR",
                    "message": "The request contains invalid data",
                    "hint": "Please check your input and try again",
                }
            },
        )
