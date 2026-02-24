from zoe_http.response import Response
from zoe_http.code import HttpCode

class ValidatorException(Exception):
    def __init__(self: "ValidatorException", field_name: str, message: str) -> None:
        self.field_name = field_name
        self.message = message
        super().__init__(message)

    def to_response(self: "ValidatorException", model_name: str) -> Response:
        return Response(http_status_code=HttpCode.BAD_REQUEST, body={
            "schema-error": {
                "error-reason": "validator error",
                "model": model_name,
                "field_name": self.field_name,
                "message": self.message
            }
        })