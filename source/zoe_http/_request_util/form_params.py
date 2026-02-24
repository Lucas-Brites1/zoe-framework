from typing import Any

class FormParams(dict):
    def __getattr__(self: "FormParams", key: str) -> str:
        return self.get(key)

    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)
