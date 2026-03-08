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
              self.instance = obj
              self.object_name: str = obj.__name__
          case ObjectKind.PRIMITIVE:
              raise ZoeNonHttpError(
                  why=f"Primitive type '{type(obj).__name__}' cannot be registered in the Container",
                  explain=f"Only classes, functions, or instances are valid. '{type(obj).__name__}' is a primitive.",
                  fix="Wrap the value in a class before registering it."
              )
          case _:
              self.instance = obj
              self.object_name: str = type(obj).__name__

    def _assert_lifecycle_compatibility(self, obj: Any, lifecycle: Lifecycle) -> None:
      if self.kind == ObjectKind.INSTANCE:
          if lifecycle is not PROVIDED:
              raise ZoeNonHttpError(
                  why=f"'{type(obj).__name__}' is an instance and cannot have a lifecycle assigned",
                  explain=f"Instances are not managed by the Container — they must use PROVIDED.",
                  fix=(
                      f"Use Container.provide_instance({type(obj).__name__}(...)) to register an existing instance,\n"
                      f"or pass the class to let the Container manage its lifecycle:\n\n"
                      f"  @Singleton\n"
                      f"  class {type(obj).__name__}: ..."
                  )
              )
      else:
          if lifecycle is PROVIDED:
              raise ZoeNonHttpError(
                  why=f"'{obj.__name__}' is a {self.kind.value} and cannot use PROVIDED lifecycle",
                  explain=f"PROVIDED is reserved for already existing instances, not classes or functions.",
                  fix=(
                      f"Use a managed lifecycle instead:\n\n"
                      f"  @Singleton  — shared instance\n"
                      f"  @Scoped     — one per request\n"
                      f"  @Transient  — new instance every time\n\n"
                      f"Example:\n"
                      f"  @Singleton\n"
                      f"  class {obj.__name__}: ..."
                  )
              )
