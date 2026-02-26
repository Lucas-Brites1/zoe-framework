from zoe_di.box import Box
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException

class Container:
    __registry: dict[str, Box] = {}

    @classmethod
    def provide(cls, box: Box) -> None:
        cls.__registry[box.key] = box.instance

    @classmethod
    def provide_many(cls, *boxes: Box) -> None:
        for box in boxes:
            cls.provide(box)

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls.__registry

    @classmethod
    def resolve(cls, key: str) -> Box:
        if not cls.has(key):
            raise InternalServerException(
                detail=f"No instance registered for '{key}'. "
                       f"Did you forget Container.provide(Box(...))?"
            )
        return cls.__registry[key]
