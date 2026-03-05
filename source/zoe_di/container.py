from zoe_di.box import Box
from zoe_di.lifecycle import PROVIDED
from zoe_di.inspector import Inspector, ObjectKind
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException
from typing import Any
class Container:
    __registry: dict[str, Box] = {}

    @classmethod
    def provide(cls, box: Box) -> None:
        registry_key: str = box.key or box.object_name
        cls.__registry[registry_key] = box

    @classmethod
    def provide_instance(cls, obj: Any, key: str | None = None) -> None:
        box = Box(obj=obj, lifecycle=PROVIDED, key=key)
        cls.provide(box=box)

    @classmethod
    def has(cls, key: str | Any) -> bool:
        key_kind = Inspector.object_kind(obj=key)
        match key_kind:
            case ObjectKind.PRIMITIVE:
                return key in cls.__registry
            case ObjectKind.CLASS:
                return key.__name__ in cls.__registry # type: ignore
            case _:
                return key.__class__.__name__ in cls.__registry

    @classmethod
    def resolve(cls, key: str | Any) -> Box:
        if not cls.has(key):
            raise InternalServerException(
                detail=f"No instance registered for '{key}'. "
                       f"Did you forget Container.provide(Box(...))?"
            )
        return cls.__registry[key]
