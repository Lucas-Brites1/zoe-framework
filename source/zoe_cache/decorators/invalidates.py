from functools import wraps
from typing import Any, Callable

from zoe_cache.cache_registry import CacheRegistry


def invalidates(*invalidate: Callable) -> Callable:
    def decorator(func: Callable) -> Callable:
        invalidate_keys: list[str] = [
            CacheRegistry.genkey(ref=ref) for ref in invalidate
        ]

        @wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            CacheRegistry.invalidate(*invalidate_keys)
            return result

        return wrapped

    return decorator
