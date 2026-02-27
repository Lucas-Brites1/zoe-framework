from zoe_schema.field_schema_validator import FieldValidator
class Field:
    def __init__(self: "Field", *validators: FieldValidator):
        self.validators: tuple[FieldValidator, ...] = validators

    def __new__(cls, *validators: FieldValidator) -> "Field":
        instance = super().__new__(cls)
        return instance
