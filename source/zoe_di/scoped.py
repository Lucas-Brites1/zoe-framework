from zoe_di.box import Box
from zoe_di.lifecycle import SCOPED
from zoe_di.container import Container
from zoe_di.inspector import Inspector
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from typing import Type, Any
from inspect import isclass, isfunction

class Scoped:
    def __init__(self, key: str | None = None, **kwargs) -> None:
        if isclass(key) or isfunction(key):
            raise ZoeNonHttpError(
                why=f"Invalid usage of @Scoped on '{key.__name__}'",
                explain=(
                    f"@Scoped was used without parentheses:\n\n"
                    f"  @Scoped\n"
                    f"  class {key.__name__}: ..."
                ),
                fix=(
                    f"Add parentheses to the decorator:\n\n"
                    f"  @Scoped()\n"
                    f"  class {key.__name__}: ...\n\n"
                    f"Or with parameters:\n"
                    f"  @Scoped(key='custom_key', param1='value1')\n"
                    f"  class {key.__name__}: ..."
                )
            )

        self.key = key
        self.params = kwargs

    def __call__(self, type_ref: Any) -> Any:
        scoped_box: Box = Box(obj=type_ref, lifecycle=SCOPED, key=self.key, params=self.params)
        Container.provide(box=scoped_box)
        return type_ref
