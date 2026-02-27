from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException

class Box:
    def __init__(self, instance: object, key: str | None = None) -> None:
        if instance is None:
            raise InternalServerException(detail="Box cannot wrap None.")

        self.instance = instance
        self.key: str = key if key else instance.__class__.__name__

        if isinstance(instance, (str, int, float, bool, list, dict, tuple)) and key is None:
            raise InternalServerException(
                detail=f"Box expects a class instance, not a primitive '{type(instance).__name__}'. "
                       f"Wrap your value in a class before boxing it."
            )

        
