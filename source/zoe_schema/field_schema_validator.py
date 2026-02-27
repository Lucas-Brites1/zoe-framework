from typing import Protocol, Any

class FieldValidator(Protocol):
    """
    Protocol (interface) that all field validators must implement.
    ---
    If the built-in validators don't cover your needs, you can create
    a custom one by implementing the `validate()` method in any class —
    no need to explicitly inherit from `FieldValidator`.

    ---

    *Required method:*
    ```python
        def validate(self, value: Any, field_name: str) -> None:
            ...
    ```

    *Raises* `SchemaValidatorException` if validation fails.
    Returns `None` if validation passes.

    ---

    *Example:*
    ```python
        from zoe import FieldValidator, Field
        from zoe_exceptions.schemas_exceptions import SchemaValidatorException

        class EvenNumber(FieldValidator):
            def validate(self, value: Any, field_name: str) -> None:
                if value % 2 != 0:
                    raise SchemaValidatorException(
                        field=field_name,
                        message=f"{field_name} must be an even number."
                    )

        class MyDto(Model):
            count: int = Field(EvenNumber())
    ```
    """
    def validate(self, value: Any, field_name: str) -> None:
        raise NotImplementedError("Validator must implement validate()")
