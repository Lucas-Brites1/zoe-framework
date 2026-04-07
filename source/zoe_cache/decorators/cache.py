from functools import wraps
from time import time
from typing import Any, Callable

from zoe_di.inspector import CallableInfo, Inspector
from zoe_exceptions.exc_internal_exc import InternalServerException, ZoeNonHttpError

from zoe_cache.cache_registry import _MISSING, CacheRegistry


def cache(ttl: int | None = None, by: str | tuple[str, ...] | None = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        func_part: str = CacheRegistry.genkey(ref=func)

        fn_info: CallableInfo = Inspector.callable_infos(fn=func, skip_self=False)
        has_self: bool = "self" in fn_info.callable_params.keys()
        by_params: tuple[str, ...] = ()

        if by is not None:
            by_params = (by,) if isinstance(by, str) else by

            for p in by_params:
                if p not in fn_info.callable_params:
                    valid_params: str = ", ".join(fn_info.callable_params.keys())

                    raise InternalServerException.from_non_http_error(
                        ZoeNonHttpError(
                            why="Invalid cache index parameter",
                            explain=f"Parameter '{p}' specified as cache index was not found in function '{fn_info.callable_name}' signature",
                            fix=f"Make sure the cache index matches a parameter name in the function: {fn_info.callable_name}({valid_params}=value)",
                        )
                    )

        param_names: list = [
            pname for pname in fn_info.callable_params.keys() if pname != "self"
        ]

        @wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            all_args: dict = dict(zip(param_names, args[1:] if has_self else args))
            all_args.update(kwargs)

            if by_params:
                vary_str: str = "&".join(
                    f"{p}={all_args[p]}" for p in by_params if p in all_args
                )
                key = f"{func_part}?{vary_str}"
            else:
                key = func_part

            cached_value = CacheRegistry.get(key=key)

            if cached_value is not _MISSING:
                value, expires_at = cached_value
                if expires_at is None or time() < expires_at:
                    return value

            result: Any = func(*args, **kwargs)
            CacheRegistry.set(key=key, value=result, ttl=ttl)
            return result

        return wrapped

    return decorator
