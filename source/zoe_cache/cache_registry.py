from threading import Lock
from time import time
from typing import Any, Callable, Type

_MISSING = object()


class CacheRegistry:
    __store: dict[str, tuple[Any, float | None]] = {}
    __lock: Lock = Lock()

    @staticmethod
    def genkey(ref: Type[Callable]) -> str:
        return f"{ref.__module__}.{ref.__qualname__}"

    @staticmethod
    def get(key: str) -> Any:
        return CacheRegistry.__store.get(key, _MISSING)

    @staticmethod
    def set(key: str, value: Any, ttl: int | None = None) -> None:
        with CacheRegistry.__lock:
            expires_at = time() + ttl if ttl is not None else None
            CacheRegistry.__store[key] = (value, expires_at)

    @staticmethod
    def invalidate(*key: str) -> None:
        with CacheRegistry.__lock:
            for k in key:
                CacheRegistry.__store.pop(k, _MISSING)
