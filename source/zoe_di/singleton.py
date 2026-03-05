from zoe_di.box import Box
from zoe_di.lifecycle import SINGLETON
from zoe_di.container import Container
from typing import Type, Any

#@Singleton
#class Database:
# == Singleton(Database)
#@Singleton.params(...)

class Singleton:
  def __new__(cls, type_ref: Type, key: str | None = None, params: dict[str, Any] | None = {}) -> "Type":
    box: Box = Box(obj=type_ref, lifecycle=SINGLETON, key=key, params=params)
    Container.provide(box)
    return type_ref

  @classmethod
  def with_params(cls, key: str | None = None, **kwargs):
    def wrapper(type_ref: Type):
      box: Box = Box(obj=type_ref, lifecycle=SINGLETON, key=key, params=kwargs)
      Container.provide(box)
      return type_ref
    return wrapper
