from typing import Protocol, Any

class FieldValidator(Protocol):
    def __call__(self: "FieldValidator", value: Any, field_name: str) -> None:
        # return None if valid and raise ValueError exception if invalid
        ...