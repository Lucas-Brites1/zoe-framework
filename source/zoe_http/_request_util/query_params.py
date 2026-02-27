from typing import Any

class QueryParams(dict):
    def __getattr__(self: "QueryParams", key: str) -> str:
        return self.get(key) #type: ignore

    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)
