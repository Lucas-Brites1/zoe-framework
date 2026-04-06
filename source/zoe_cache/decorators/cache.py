from functools import wraps
from time import time
from typing import Any, Callable

from zoe_cache.cache_registry import _MISSING, CacheRegistry


def cache(ttl: int | None = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        cached_key: str = CacheRegistry.genkey(ref=func)

        @wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            cached_value = CacheRegistry.get(key=cached_key)

            if cached_value is not _MISSING:
                value, expires_at = cached_value
                if expires_at is None or time() < expires_at:
                    return value
                CacheRegistry.invalidate(cached_key)

            result: Any = func(*args, **kwargs)
            CacheRegistry.set(key=cached_key, value=result, ttl=ttl)
            return result

        return wrapped

    return decorator
