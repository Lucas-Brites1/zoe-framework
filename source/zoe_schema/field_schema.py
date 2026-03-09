from zoe_schema.field_schema_validator import FieldValidator
from typing import Any
class  _Field:
    def __init__(self: "_Field", *validators: FieldValidator, default: Any | None = None, required: bool = False) -> None:
        self.validators: list[FieldValidator] = list(validators) if validators else []
        self.is_required = required
        self.default_value = default

def Field(*validators: FieldValidator, default: Any | None = None, required: bool = False) -> Any:
    return _Field(*validators, default=default, required=required)
