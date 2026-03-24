from typing import Any, Type
from functools import wraps
from zoe_di.inspector import Inspector, ObjectKind, CallableInfo, ParamInfo
from zoe_di.container import Container
from zoe_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_schema.model_schema import Model
from enum import Enum

class _InjectableBy(Enum):
    NAME = "injectable by name"
    TYPE = "injectable by type"

class _AnalysedVar:
    def __init__(self, var_name: str, var_type: type[Any], resolved_by: _InjectableBy) -> None:
        self.name = var_name
        self.type_ = var_type
        self.resolved_by = resolved_by

    def __str__(self) -> str:
        scope = (
            "dunder" if self.name.startswith('__') and self.name.endswith('__')
            else "private" if self.name.startswith('_')
            else "public"
        )

        type_name = getattr(self.type_, '__name__', repr(self.type_))

        return f"Field<{scope}>: {self.name}: {type_name} ({self.resolved_by.value})"

    def __repr__(self) -> str:
        return self.__str__()


class _AnalysedParam:
    def __init__(self, param_name: str, param_info: ParamInfo, resolved_by: _InjectableBy):
        self.name = param_name
        self.infos = param_info
        self.resolved_by = resolved_by

    def __str__(self) -> str:
        return f"<{self.name}: {self.infos.param_type.__name__}> [{self.resolved_by.value}]" # type: ignore

    def __repr__(self) -> str:
        return self.__str__()

class _AnalysedMethod:
    def __init__(self, method_name: str, method_info: CallableInfo):
        self.name = method_name
        self.info = method_info
        self.injectable_params: list[_AnalysedParam] = []

    def add_param(self, param: _AnalysedParam):
        self.injectable_params.append(param)

    @property
    def has_injectable_params(self) -> bool:
        return len(self.injectable_params) > 0

    def __str__(self) -> str:
        if not self.injectable_params:
            return f"Method: {self.name} | Injectable params: 0"

        visibility = (
            "constructor" if self.name == '__init__'
            else "dunder" if self.name.startswith('__') and self.name.endswith('__')
            else "private" if self.name.startswith('_')
            else "public"
        )

        count = len(self.injectable_params)
        params_list = ", ".join(str(p) for p in self.injectable_params)

        return (
            f"Method: {self.name}\n"
            f"Scope: {visibility}\n"
            f"Injectable params: {count}\n"
            f"Parameters: [{params_list}]"
        )

    @staticmethod
    def from_callable_info(callable_info: CallableInfo) -> "_AnalysedMethod":
        """Factory method to instantiate from CallableInfo"""
        return _AnalysedMethod(
            method_name=callable_info.callable_name,
            method_info=callable_info
        )

class Injectable:
    _PYTHON_MAGIC_ATTRS = frozenset({
            '__module__', '__dict__', '__weakref__', '__doc__',
            '__annotations__', '__firstlineno__', '__static_attributes__',
            '__qualname__', '__slots__', '__class__', '__bases__',
            '__mro__', '__subclasses__', '__init_subclass__',
            '__new__', '__hash__', '__eq__', '__ne__', '__lt__',
            '__le__', '__gt__', '__ge__', '__repr__', '__str__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dir__', '__sizeof__', '__reduce__', '__reduce_ex__',
            '__getstate__', '__setstate__', '__format__',
            '__subclasshook__', '__instancecheck__', '__subclasscheck__'
        })

    def __new__(cls, wrapped: Type):
        kind: ObjectKind = Inspector.object_kind(wrapped)
        if kind != ObjectKind.CLASS:
            what_was_passed = (
                f"function '{wrapped.__name__}'" if kind == ObjectKind.FUNC
                else f"instance of '{type(wrapped).__name__}'" if kind == ObjectKind.INSTANCE
                else f"{kind.value}"
            )

            raise InternalServerException.from_non_http_error(
                ZoeNonHttpError(
                    why=f"@Injectable can only be applied to classes",
                    explain=(
                        f"You tried to decorate a {what_was_passed}, but @Injectable "
                        f"only works with class definitions.\n\n"
                        f"@Injectable is designed to enable automatic dependency injection "
                        f"for class constructors and methods."
                    ),
                    fix=(
                        f"Use @Injectable only on classes:\n\n"
                        f"  > Correct:\n"
                        f"  \t@Injectable\n"
                        f"  \tclass MyService:\n"
                        f"    \tdef __init__(self, db: DatabaseService):\n"
                        f"          ...\n\n"
                        f"  > Incorrect:\n"
                        f"  \t@Injectable\n"
                        f"  \tdef my_function():  # <- Not allowed!\n"
                        f"      ..."
                    )
                )
            )

        if issubclass(wrapped, Model):
            raise InternalServerException.from_non_http_error(
                ZoeNonHttpError(
                    why=f"@Injectable cannot be used on Model classes",
                    explain=(
                        f"'{wrapped.__name__}' inherits from Model, which is designed for "
                        f"data transfer objects (DTOs) that represent request/response payloads.\n"
                        f"Models should only contain data fields, not injected dependencies. "
                        f"Mixing DTOs with dependency injection violates separation of concerns "
                        f"and can cause serialization issues."
                    ),
                    fix=(
                        f"Option 1 - Use a separate service class:\n"
                        f"  # DTO (data only)\n"
                        f"  class {wrapped.__name__}(Model):\n"
                        f"      name: str\n"
                        f"      email: str\n\n"
                        f"  # Service (with dependencies)\n"
                        f"  @Injectable\n"
                        f"  class {wrapped.__name__}Service:\n"
                        f"      def __init__(self, db: DatabaseService):\n"
                        f"          self.db = db\n\n"
                        f"      def create_user(self, data: {wrapped.__name__}):\n"
                        f"          return self.db.save(data)\n\n"
                        f"Option 2 - If you need dependencies, don't inherit from Model:\n\n"
                        f"  @Injectable\n"
                        f"  class {wrapped.__name__}:  # Not a Model\n"
                        f"      def __init__(self, db: DatabaseService):\n"
                        f"          ..."
                    )
                )
            )


        internal_variables: dict[str, type[Any]] = cls.__resolve_internal_variables(kind=kind, ref=wrapped)
        internal_wrapped_callables: list[CallableInfo] | None = cls.__capture_internal_functions(ref=wrapped) or []

        analyzed_methods: list[_AnalysedMethod] = cls.__analyze_injectable_params(internal_methods=internal_wrapped_callables)
        analyzed_vars: list[_AnalysedVar] = cls.__analyze_injectable_variables(internal_variables=internal_variables)

        dependencies_count: int = (
            len(analyzed_vars) +
            sum(len(m.injectable_params) for m in analyzed_methods)
        )

        if not dependencies_count:
            raise InternalServerException.from_non_http_error(
                error=ZoeNonHttpError(
                    why=f"'{wrapped.__name__}' is decorated with @Injectable but has no injectable parameters or attributes",
                    explain=(
                        f"@Injectable wraps class methods to enable automatic dependency injection.\n"
                        f"This involves runtime overhead for method interception and parameter resolution.\n"
                        f"'{wrapped.__name__}' has no parameters or fields registered in the Container, "
                        f"so the decorator adds unnecessary processing cost without providing any functionality."
                    ),
                     fix=(
                        f"Option 1 - Remove the decorator:\n"
                        f"  class {wrapped.__name__}:  # No @Injectable needed\n"
                        f"      ...\n\n"
                        f"Option 2 - Add injectable dependencies:\n"
                        f"  # Register dependencies in Container\n"
                        f"  @Singleton(...)\n"
                        f"  class DatabaseService:\n"
                        f"      ...\n\n"
                        f"  # Or provide instances with keys\n"
                        f"  Container.provide_instance(CacheService(...), key='cache')\n\n"
                        f"  # Then use @Injectable\n"
                        f"  @Injectable\n"
                        f"  class {wrapped.__name__}:\n"
                        f"      cache: CacheService  # Injected by key 'cache'\n\n"
                        f"      def __init__(self, db: DatabaseService):  # Injected by type\n"
                        f"          ..."
                        )
                    )
                )

        for method in analyzed_methods:
            if method.has_injectable_params:
                cls.wrap_method(method=method, target_class=wrapped)

        cls.wrap_vars(analyzed_vars=analyzed_vars, target_class=wrapped)

        return wrapped

    @classmethod
    def __capture_internal_functions(cls, ref: Type) -> list[CallableInfo] | None:
        result: list[CallableInfo] | None = Inspector.get_internal_methods_info(
              obj=ref,
              skip_fields=Injectable._PYTHON_MAGIC_ATTRS
        )
        return [] if result is None else result

    @classmethod
    def __resolve_internal_variables(cls, kind: ObjectKind, ref: Type) -> dict[str, type[Any]]:
        if kind != ObjectKind.CLASS:
            return {}

        vars_: dict[str, Any] = Inspector.get_annotations(obj=ref)
        return vars_

    @classmethod
    def __analyze_injectable_variables(cls, internal_variables: dict[str, type[Any]]) -> list[_AnalysedVar]:
        analysed_vars: list[_AnalysedVar] = []
        for name_, type_ in internal_variables.items():

            if Container.has(name_):
                analysed_vars.append(
                    _AnalysedVar(
                        var_name=name_,
                        var_type=type_,
                        resolved_by=_InjectableBy.NAME
                    )
                )
                continue

            elif Container.has(type_):
                analysed_vars.append(
                    _AnalysedVar(
                        var_name=name_,
                        var_type=type_,
                        resolved_by=_InjectableBy.TYPE
                    )
                )


        return analysed_vars

    @classmethod
    def __analyze_injectable_params(cls, internal_methods: list[CallableInfo]) -> list[_AnalysedMethod]:
        analyzed_methods: list[_AnalysedMethod] = []

        for method in internal_methods:
            current_method: _AnalysedMethod = _AnalysedMethod(
                    method_name=method.callable_name,
                    method_info=method
                )

            analyzed_methods.append(current_method)

            for param_name, param_info in method.callable_params.items():

                if Container.has(ref=param_name):
                    current_method.add_param(
                        _AnalysedParam(
                            param_name=param_name,
                            param_info=param_info,
                            resolved_by=_InjectableBy.NAME
                        )
                    )
                    continue

                elif Container.has(ref=param_info.param_type):
                    current_method.add_param(
                        _AnalysedParam(
                            param_name=param_name,
                            param_info=param_info,
                            resolved_by=_InjectableBy.TYPE
                        )
                    )

        return analyzed_methods

    @classmethod
    def wrap_method(cls, target_class: type[Any], method: _AnalysedMethod) -> None:
        original_method = getattr(target_class, method.name)

        @wraps(original_method)
        def new_method(self, *args, **kwargs):
            for param in method.injectable_params:
                if param.name in kwargs:
                    continue

                if param.resolved_by == _InjectableBy.NAME:
                    kwargs[param.name] = Container.resolve(ref=param.name)
                else:
                    kwargs[param.name] = Container.resolve(ref=param.infos.param_type)

            return original_method(self, *args, **kwargs)

        new_annotations: dict = original_method.__annotations__.copy()
        for param in method.injectable_params:
            new_annotations.pop(param.name, None)

        new_method.__annotations__ = new_annotations

        setattr(target_class, method.name, new_method)

    @classmethod
    def wrap_vars(cls, target_class: type[Any], analyzed_vars: list[_AnalysedVar]) -> None:
        original_init = target_class.__init__

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)

            for var in analyzed_vars:
                if var.resolved_by == _InjectableBy.NAME:
                    setattr(self, var.name, Container.resolve(ref=var.name))
                else:
                    setattr(self, var.name, Container.resolve(ref=var.type_))

        target_class.__init__ = new_init
