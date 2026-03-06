from zoe_di.box import Box
from zoe_di.lifecycle import TRANSIENT, SINGLETON, PROVIDED, Lifecycle
from zoe_di.inspector import Inspector, ObjectKind
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_non_http_aggregate import ZoeNonHttpAggregate
from typing import Any, TypeAlias
import uuid
#TERMINAR SCOPED VER COMO CRIAR E TERMINAR CORRETAMENTE VER SE NO CONTEXTO DA MESMA REQUISICAO CONTINUA SENDO A MESMA INSTANCIA E EM OUTRA COMPARAR A DA REQUISICAO 1 COM A REQUISICAO 2

Keyref: TypeAlias = str | type | Any

class Container:
    __registry: dict[str, Box] = {}
    __singleton_instances: dict[str, Any] = {}
    __scoped_instances: dict[str, dict[str, Any]] = {}

    @classmethod
    def provide(cls, box: Box) -> None:
        print("Container Debug (PROVIDE)\n")

        key: str = cls.__normalize_box_key(box)
        if key in cls.__registry:
            raise ZoeNonHttpError(
                exception_message=(
                    f"Key '{key}' is already registered.\n"
                    f"Existing: {cls.__registry[key].object_name}\n"
                    f"Attempted: {box.object_name}"
                )
            )

        print(f"Key: {key}")
        cls.__registry[key] = box

    @classmethod
    def provide_instance(cls, obj: Any, key: str | None = None) -> None:
        box = Box(obj=obj, lifecycle=PROVIDED, key=key)
        cls.provide(box=box)

    @classmethod
    def has(cls, ref: Keyref) -> bool:
        try:
            key = cls.__get_lookup_key(ref)
            return key in cls.__registry
        except ZoeNonHttpError:
            return False

    @classmethod
    def __get_lookup_key(cls, ref: Keyref) -> str:
        key_kind = Inspector.object_kind(obj=ref)

        match key_kind:
            case ObjectKind.PRIMITIVE:
                if isinstance(ref, str):
                    return ref
                raise ZoeNonHttpError(
                    exception_message=f"Primitive type '{type(ref).__name__}' cannot be used as key"
                )
            case ObjectKind.CLASS | ObjectKind.FUNC:
                return ref.__name__

            case ObjectKind.INSTANCE:
                return type(ref).__name__

            case _:
                raise ZoeNonHttpError(
                exception_message=f"Cannot determine key for type '{type(ref).__name__}'"
            )

    @classmethod
    def resolve(cls, ref: Keyref) -> Any:
        key: str = cls.__resolve_key(ref)
        print(F"Resolve: {key}")

        if key not in cls.__registry:
            available = ', '.join(f"'{k}'" for k in cls.__registry.keys())
            raise ZoeNonHttpError(
                exception_message=(
                    f"Key '{key}' not found in Container.\n"
                    f"Available keys: [{available or 'none'}]\n"
                    f"Did you forget to register it?"
                )
            )
        
        resolved_box: Box =  cls.__registry[key]
        return cls.__resolve_dependency(box=resolved_box, key=key)

    @classmethod
    def __resolve_constructor_params(cls, box: Box) -> tuple[dict[str, Any], list[ZoeNonHttpError]]:
        kwargs: dict[str, Any] = {}
        errors: list[ZoeNonHttpError] = []

        for pname, pvalue in box.info.callable_params.items():
            if pname not in box.provided_params:

                if pvalue.param_is_required:
                    errors.append(
                                ZoeNonHttpError(
                                    exception_message=(
                                        f"Cannot instantiate {box.object_name}: missing '{pname}'\n\n"
                                        f"Your code:\n"
                                        f"  @{box.lifecycle.value.capitalize()}\n"
                                        f"  class {box.object_name}:\n"
                                        f"      def __init__(self, {pname}): ...  <- needs a value!\n\n"
                                        f"Fix:\n"
                                        f"  @{box.lifecycle.value.capitalize()}({pname}='your_value')\n"
                                        f"  class {box.object_name}: ...\n\n"
                                        f"  or provide a default value:\n"
                                        f"  def __init__(self, {pname}='default_value'): ..."
                                    )
                                )
                            )
                continue
            
            else:
                kwargs[pname] = box.provided_params[pname]
            
        return (kwargs, errors)

    @classmethod
    def __resolve_dependency(cls, box: Box, key: str) -> Any:
        errors: list[ZoeNonHttpError] = []

        match box.lifecycle:
            case Lifecycle.PROVIDED:
                return box.instance
            case Lifecycle.SINGLETON:
                cached: Any = cls.__singleton_instances.get(key)
                if cached is not None:
                    return cached
                
        params, params_errors = cls.__resolve_constructor_params(box)

        if errors:
            raise ZoeNonHttpAggregate(errors=params_errors)
        
        dependency: Any = cls.__create_instance(box, params)

        if box.lifecycle is Lifecycle.SINGLETON:
            cls.__singleton_instances[key] = dependency
        
        return dependency

    @classmethod
    def __create_instance(cls, box: Box, params: dict[str, Any]) -> Any: 
        match box.kind:
            case ObjectKind.CLASS:
                return box.instance(**params)

            case ObjectKind.FUNC:
                return box.info.callable_ref(**params)

            case _:
                raise ZoeNonHttpError(
                    exception_message=f"Cannot create instance for kind: {box.kind}"
                ) 

    @classmethod
    def __create_scope(cls, box: Box, params: dict[str, Any]) -> str: # retorna o ID
        scope_id: str = str(uuid.uuid4())
        cls.__scoped_instances[scope_id] = cls.__create_instance(box, params)
        return scope_id

    @classmethod
    def __end_scope(cls, scope_id: str):
        if scope_id in cls.__scoped_instances:
            del cls.__scoped_instances[scope_id]

    @classmethod
    def __normalize_box_key(cls, box: Box) -> str:
        if box.key is not None:
            return box.key
        
        if box.object_name:
            return box.object_name
        
        if box.info.callable_name:
            return box.info.callable_name

        raise ZoeNonHttpError(
            exception_message=f"Cannot determine key for Box with kind {box.kind}"
        )

    @classmethod
    def __resolve_key(cls, ref: Keyref) -> str:
        if isinstance(ref, Box):
            return cls.__normalize_box_key(box=ref)

        if isinstance(ref, str):
            return ref

        kind: ObjectKind = ObjectKind.from_object(object=ref)

        match kind:
            case ObjectKind.FUNC | ObjectKind.CLASS:
                return ref.__name__

            case ObjectKind.INSTANCE:
                return type(ref).__name__

            case ObjectKind.PRIMITIVE:
                raise ZoeNonHttpError(
                    exception_message=(
                        f"Primitive type '{type(ref).__name__}' cannot be used as Container key.\n"
                        f"Use a string key instead: Container.resolve('my_key')"
                    )
                )

            case _:
                raise ZoeNonHttpError(
                    exception_message=f"Cannot resolve key for unknown type: {type(ref).__name__}"
                )