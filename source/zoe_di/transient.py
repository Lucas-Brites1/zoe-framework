from zoe_di.box import Box
from zoe_di.lifecycle import TRANSIENT
from zoe_di.container import Container
from zoe_di.inspector import Inspector
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from typing import Type, Any
from inspect import isclass, isfunction

class Transient:
    def __init__(self, key: str | None = None, **kwargs):
        if isclass(key) or isfunction(key):
            raise ZoeNonHttpError(
                exception_message=(
                    f"Invalid usage of @Transient decorator\n\n"
                    f"You wrote:\n"
                    f"  @Transient\n"
                    f"  class {key.__name__}: ...\n\n"
                    f"Correct usage:\n"
                    f"  @Transient()  # <- Add parentheses!\n"
                    f"  class {key.__name__}: ...\n\n"
                    f"Or with parameters:\n"
                    f"  @Transient(key='custom_key', param1='value1', param2='value2' ...)\n"
                    f"  class {key.__name__}: ...\n"
                )
            )

        self.key = key
        self.params = kwargs
    
    def __call__(self, type_ref: Any) -> Any:
        factory_box: Box = Box(obj=type_ref, lifecycle=TRANSIENT, key=self.key, params=self.params)
        Container.provide(box=factory_box)
        return type_ref 