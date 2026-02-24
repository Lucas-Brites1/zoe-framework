from zoe_http.response import Response
from zoe_http.code import HttpCode

class SchemaFieldUnexpectedType(Exception):
    def __init__(self: "SchemaFieldUnexpectedType", field_name: str, field_expected_type: type, field_actual_type: type) -> None:
        self.field_name = field_name
        self.field_expected_type = field_expected_type
        self.field_actual_type = field_actual_type

    def to_response(self: "SchemaFieldUnexpectedType", model_name: str) -> Response:
        return Response(
            http_status_code=HttpCode.BAD_REQUEST,
            body={
                "schema-error": {
                    "error-reason": "unexpected field type",
                    "model": model_name,
                    "field": self.field_name,
                    "expected-type": self.field_expected_type.__name__,
                    "actual-type": self.field_actual_type.__name__
                }
            })