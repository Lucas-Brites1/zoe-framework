from zoe_di.box import Box
from zoe_di.lifecycle import SINGLETON
from zoe_di.container import Container
from zoe_di.inspector import Inspector
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from typing import Type, Any
from inspect import isclass, isfunction

#@Singleton
#class Database:
# == Singleton(Database)
#@Singleton.params(...)

class Singleton:
  def __init__(self, key: str | None = None, **kwargs) -> Any:
    if isclass(key) or isfunction(key):
            raise ZoeNonHttpError(
                exception_message=(
                    f"Invalid usage of @Singleton decorator\n\n"
                    f"You wrote:\n"
                    f"  @Singleton\n"
                    f"  class {key.__name__}: ...\n\n"
                    f"Correct usage:\n"
                    f"  @Singleton()  # <- Add parentheses!\n"
                    f"  class {key.__name__}: ...\n\n"
                    f"Or with parameters:\n"
                    f"  @Singleton(key='custom_key', param1='value1', param2='value2' ...)\n"
                    f"  class {key.__name__}: ...\n"
                )
            )

    self.params = kwargs
    self.key = key
  
  def __call__(self, type_ref: Any) -> Any:
    singleton_box = Box(obj=type_ref, lifecycle=SINGLETON, key=self.key, params=self.params)
    Container.provide(singleton_box)
    return type_ref
   