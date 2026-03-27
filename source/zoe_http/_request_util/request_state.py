from typing import Any

class RequestState:
    def __init__(self, initial: dict[str, Any] | None = None):
        super().__setattr__("_states", {})
        if initial:
            self._states.update(initial)

    def __setattr__(self, name: str, value: Any):
        self._states[name] = value

    def __getattr__(self, name: str) -> Any:
        return self._states.get(name, None)

    def __contains__(self, name: str) -> bool:
        return name in self._states

    def get(self, name: str, default: Any = None) -> Any:
        return self._states.get(name, default)

    def set(self, name: str, value: Any) -> None:
        self._states[name] = value

    def to_dict(self) -> dict[str, Any]:
        return dict(self._states)
