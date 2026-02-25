from zoe_schema.field_schema_validator import FieldValidator
from zoe_exceptions.schemas_exceptions.validation_exception import ValidatorException
from typing import Any

class NotNull(FieldValidator):
    def __call__(self, value: Any, field_name: str) -> None:
        if value is None:
            raise ValidatorException(field_name=field_name, message=f"'{field_name}' cannot be null")
