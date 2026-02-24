from zoe_schema.field_schema_validator import FieldValidator
class Field:
    def __init__(self: "Field", *validator: FieldValidator) -> None:
        self.validators: list[FieldValidator] = validator
