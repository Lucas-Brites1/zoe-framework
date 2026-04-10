import threading
from functools import wraps
from typing import Callable, TypeVar, overload

from zoe_di.inspector import Inspector, ObjectKind

_local = threading.local()

C = TypeVar("C", bound=type)
F = TypeVar("F", bound=Callable)


@overload
def loggable(cls_or_func: C) -> C: ...
@overload
def loggable(cls_or_func: F) -> F: ...
def loggable(cls_or_func: C | F) -> C | F:
    kind: ObjectKind = Inspector.object_kind(obj=cls_or_func)
    if kind == ObjectKind.CLASS:
        original_init: Callable = cls_or_func.__init__  # type: ignore

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            _local.context = cls_or_func.__qualname__
            original_init(self, *args, **kwargs)

        cls_or_func.__init__ = new_init  # type: ignore
        return cls_or_func
    else:

        @wraps(cls_or_func)  # type: ignore
        def new_func(*args, **kwargs):
            _local.context = cls_or_func.__qualname__  # type: ignore
            return cls_or_func(*args, **kwargs)  # type: ignore

        return new_func  # type: ignore


def subloggable(fn: F) -> F:
    kind: ObjectKind = Inspector.object_kind(obj=fn)
    if kind != ObjectKind.FUNC:
        raise ValueError("subloggable can only be used on functions")

    @wraps(fn)
    def wrapped(*args, **kwargs):
        _local.subcontext = fn.__qualname__
        return fn(*args, **kwargs)

    return wrapped  # type: ignore
