from zoe_schema.field_schema_validator import FieldValidator
from typing import Any
class Field:
    def __init__(self: "Field", *validators: FieldValidator, default: Any | None = None, required: bool = False):
        self.validators: list[FieldValidator] = list(validators) if validators else []
        self.is_required = required
        self.default_value = default
