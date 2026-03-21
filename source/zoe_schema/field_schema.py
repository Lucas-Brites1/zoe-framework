from zoe_schema.field_schema_validator import FieldValidator
from zoe_schema.field_schema_generator import FieldGenerator
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_internal_exc import InternalServerException
from typing import Any

class  _Field:
    def __init__(self: "_Field", *validators: FieldValidator, generator: FieldGenerator | None = None, default: Any | None = None, required: bool = False) -> None:
        self.validators: list[FieldValidator] = list(validators) if validators else []
        self.generator: FieldGenerator | None = generator
        self.is_required = required
        self.default_value = default
        self._validate_mutual_exclusion()

    @property
    def has_generator(self) -> bool:
        return self.generator is not None

    @property
    def has_validators(self) -> bool:
        return len(self.validators) > 0

    def _validate_mutual_exclusion(self):
        if self.has_generator and self.default_value is not None:
            raise InternalServerException.from_non_http_error(ZoeNonHttpError(
                why="Field cannot have both 'generator' and 'default' set\n",
                explain="'generator' and 'default' are mutually exclusive.\n"
                "Both serve the same purpose: providing a value when the field is absent from the request body.\n"
                "Having both creates ambiguity over which one takes precedence.",
                fix="Use 'generator' if the value should be produced automatically (e.g. UUID, timestamp)."
                    "\nUse 'default' if the value should be a fixed fallback. Remove one of them."
            ))

        if self.has_generator and self.has_validators:
            raise InternalServerException.from_non_http_error(ZoeNonHttpError(
                why="Field cannot have both 'generator' and validators set",
                explain="'generator' and validators are mutually exclusive.\nA generator always produces a value internally, so there is nothing to validate from the outside.\nValidators are meant for values that come from the request body, not for generated ones.",
                fix="Remove the validators from this field, or remove the generator and handle value production elsewhere."
            ))

def Field(*validators: FieldValidator, generator: FieldGenerator | None = None,default: Any | None = None, required: bool = False) -> Any:
    return _Field(*validators, generator=generator, default=default, required=required)
