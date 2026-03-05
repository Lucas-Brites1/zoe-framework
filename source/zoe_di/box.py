from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_di.lifecycle import PROVIDED, SINGLETON, SCOPED, TRANSIENT, Lifecycle
from zoe_di.inspector import Inspector, ParamInfo, CallableInfo, ObjectKind
from typing import Callable, Type, Any
class Box:
    def __init__(self, obj: Type | Any, lifecycle: Lifecycle = PROVIDED, key: str | None = None, params: dict[str, Any] | None = None) -> None:
        self.kind: ObjectKind = Inspector.object_kind(obj)
        self.instance: Any | None = None
        self.info: CallableInfo | None = None

        self.lifecycle: Lifecycle = lifecycle
        self.key = key or None
        self.provided_params: dict[str, Any] = params or {}

        self._validate_kind(obj)
        self._assert_lifecycle_compatibility(obj=obj, lifecycle=lifecycle)

    def _validate_kind(self, obj: Type) -> None:
      match self.kind:
            case ObjectKind.FUNC:
                self.info = Inspector.callable_infos(fn=obj)
                self.object_name: str = self.info.callable_name
            case ObjectKind.CLASS:
                self.info = Inspector.callable_infos(fn=obj.__init__)
                self.object_name: str = obj.__name__
            case ObjectKind.PRIMITIVE:
                raise ZoeNonHttpError(
                    exception_message=(
                        f"Primitive types cannot be registered directly in the Container. "
                        f"'{type(obj).__name__}' is a primitive type. "
                        f"Wrap it in a class before registering it."
                    )
                )
            case _:
                self.instance = obj
                self.object_name: str = type(obj).__name__

    def _assert_lifecycle_compatibility(self, obj: Any, lifecycle: Lifecycle) -> None:
        if self.kind == ObjectKind.INSTANCE:
          if lifecycle is not PROVIDED:
            raise ZoeNonHttpError(
                exception_message=(
                    f"'{type(obj).__name__}' is already an instance and cannot be assigned a lifecycle.\n"
                    f"Instances must use 'PROVIDED' — they are not managed by the Container.\n\n"
                    f"If you want the Container to manage the lifecycle, pass the class instead:\n"
                    f"  @Singleton\n"
                    f"  class {type(obj).__name__}: ...\n\n"
                    f"If you want to provide an existing instance, use:\n"
                    f"  @Provide\n"
                    f"  {type(obj).__name__}(...)"
                )
            )
        else:
            if lifecycle is PROVIDED:
                raise ZoeNonHttpError(
                    exception_message=(
                        f"'{obj.__name__}' is a {self.kind.value} and cannot use 'PROVIDED' lifecycle.\n"
                        f"'PROVIDED' is reserved for already existing instances.\n\n"
                        f"To register a {self.kind.value}, use a managed lifecycle instead:\n"
                        f"  @Singleton  — single instance shared across the Container\n"
                        f"  @Scoped     — one instance per scope\n"
                        f"  @Transient  — new instance every time it's requested\n\n"
                        f"Example:\n"
                        f"  @Singleton\n"
                        f"  class {obj.__name__}: ..."
                    )
                )
