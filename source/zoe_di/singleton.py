from zoe_di.box import Box
from zoe_di.lifecycle import SINGLETON
from zoe_di.container import Container
from zoe_di.inspector import Inspector
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from typing import Type, Any, TypeVar
from inspect import isclass, isfunction

T = TypeVar('T')

class Singleton:
    def __init__(self, key: str | None = None, **kwargs) -> None:
        if isclass(key) or isfunction(key):
            raise ZoeNonHttpError(
                why=f"Invalid usage of @Singleton on '{key.__name__}'",
                explain=(
                    f"@Singleton was used without parentheses:\n\n"
                    f"  @Singleton\n"
                    f"  class {key.__name__}: ..."
                ),
                fix=(
                    f"Add parentheses to the decorator:\n\n"
                    f"  @Singleton()\n"
                    f"  class {key.__name__}: ...\n\n"
                    f"Or with parameters:\n"
                    f"  @Singleton(key='custom_key', param1='value1')\n"
                    f"  class {key.__name__}: ..."
                )
            )

        self.params = kwargs
        self.key = key

    def __call__(self, type_ref: type[T]) -> type[T]:
        singleton_box = Box(obj=type_ref, lifecycle=SINGLETON, key=self.key, params=self.params)
        Container.provide(singleton_box)
        return type_ref
