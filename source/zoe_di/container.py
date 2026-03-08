from zoe_di.box import Box
from zoe_di.lifecycle import TRANSIENT, SINGLETON, PROVIDED, Lifecycle
from zoe_di.inspector import Inspector, ObjectKind
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_non_http_aggregate import ZoeNonHttpAggregate
from typing import Any, TypeAlias
import uuid

Keyref: TypeAlias = str | type | Any

class Container:
    __registry: dict[str, Box] = {}
    __singleton_instances: dict[str, Any] = {}
    __scoped_instances: dict[str, dict[str, Any]] = {}

    @classmethod
    def provide(cls, box: Box) -> None:
        key: str = cls.__normalize_box_key(box)
        if key in cls.__registry:
            raise ZoeNonHttpError(
                why=f"Duplicate registration for key '{key}'",
                explain=(
                    f"Key '{key}' is already registered.\n"
                    f"Existing:  {cls.__registry[key].object_name}\n"
                    f"Attempted: {box.object_name}"
                ),
                fix=(
                    f"Remove the duplicate registration of '{key}',\n"
                    f"or use a different key for one of them."
                )
            )

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
                    why=f"Invalid key type '{type(ref).__name__}'",
                    explain=f"Primitive type '{type(ref).__name__}' cannot be used as a Container key.",
                    fix="Use a string key instead: Container.resolve('my_key')"
                )
            case ObjectKind.CLASS | ObjectKind.FUNC:
                return ref.__name__  # type: ignore

            case ObjectKind.INSTANCE:
                return type(ref).__name__

            case _:
                raise ZoeNonHttpError(
                    why=f"Cannot determine key for type '{type(ref).__name__}'",
                    explain=f"The object of type '{type(ref).__name__}' is not a valid Container key.",
                    fix="Use a class, function, or string as the key."
                )

    @classmethod
    def resolve(cls, ref: Keyref) -> Any:
        key: str = cls.__resolve_key(ref)

        if key not in cls.__registry:
            available = ', '.join(f"'{k}'" for k in cls.__registry.keys())
            raise ZoeNonHttpError(
                why=f"Key '{key}' not found in Container",
                explain=(
                    f"No dependency registered under the key '{key}'.\n"
                    f"Available keys: [{available or 'none'}]"
                ),
                fix=(
                    f"Register the dependency before starting the server:\n\n"
                    f"  @Singleton\n"
                    f"  class {key}: ...\n\n"
                    f"  or manually:\n"
                    f"  Container.provide_instance({key}(...), key='{key}')"
                )
            )

        resolved_box: Box = cls.__registry[key]
        return cls.__resolve_dependency(box=resolved_box, key=key)

    @classmethod
    def __resolve_constructor_params(cls, box: Box) -> tuple[dict[str, Any], list[ZoeNonHttpError]]:
        kwargs: dict[str, Any] = {}
        errors: list[ZoeNonHttpError] = []

        for pname, pvalue in box.info.callable_params.items():  # type: ignore
            if pname not in box.provided_params:
                if pvalue.param_is_required:
                    errors.append(
                        ZoeNonHttpError(
                            why=f"Cannot instantiate {box.object_name}: missing '{pname}'",
                            explain=(
                                f"@{box.lifecycle.value.capitalize()}\n"
                                f"class {box.object_name}:\n"
                                f"    def __init__(self, {pname}): ...  <- needs a value!"
                            ),
                            fix=(
                                f"@{box.lifecycle.value.capitalize()}({pname}='your_value')\n"
                                f"class {box.object_name}: ...\n\n"
                                f"or provide a default value:\n"
                                f"def __init__(self, {pname}='default_value'): ..."
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

        if params_errors:
            raise ZoeNonHttpAggregate(errors=params_errors)

        dependency: Any = cls.__create_instance(box, params)

        if box.lifecycle is Lifecycle.SINGLETON:
            cls.__singleton_instances[key] = dependency

        return dependency

    @classmethod
    def __create_instance(cls, box: Box, params: dict[str, Any]) -> Any:
        match box.kind:
            case ObjectKind.CLASS:
                return box.instance(**params)  # type: ignore

            case ObjectKind.FUNC:
                return box.info.callable_ref(**params)  # type: ignore

            case _:
                raise ZoeNonHttpError(
                    why=f"Cannot create instance for kind '{box.kind}'",
                    explain=f"The Box kind '{box.kind}' is not supported for instance creation.",
                    fix="Use a class or function when registering dependencies."
                )

    @classmethod
    def __create_scope(cls, box: Box, params: dict[str, Any]) -> str:
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

        if box.info.callable_name:  # type: ignore
            return box.info.callable_name  # type: ignore

        raise ZoeNonHttpError(
            why=f"Cannot determine key for Box with kind '{box.kind}'",
            explain=f"The Box has no key, object_name, or callable_name to use as a registry key.",
            fix=(
                f"Provide an explicit key when registering:\n\n"
                f"  Container.provide_instance(my_obj, key='my_key')"
            )
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
                    why=f"Primitive type '{type(ref).__name__}' cannot be used as Container key",
                    explain=f"Values of type '{type(ref).__name__}' are not valid Container keys.",
                    fix="Use a string key instead: Container.resolve('my_key')"
                )

            case _:
                raise ZoeNonHttpError(
                    why=f"Cannot resolve key for unknown type '{type(ref).__name__}'",
                    explain=f"The object of type '{type(ref).__name__}' could not be mapped to a Container key.",
                    fix="Use a class, function, instance, or string as the ref."
                )
