from typing import Callable, ParamSpec, Type, TypeVar

from zoe_di.inspector import CallableInfo, Inspector, ParamInfo
from zoe_schema.model_schema import Model

P = ParamSpec("P")
R = TypeVar("R")


def ensure_model(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        infos: CallableInfo = Inspector.callable_infos(fn=fn, skip_self=True)
        params: dict[str, ParamInfo] = infos.callable_params

        for pname, pinfo in params.items():
            ptype: Type | None = pinfo.param_type
            if ptype is None:
                continue

            if not (isinstance(ptype, type) and issubclass(ptype, Model)):
                continue

            bound: dict = dict(zip(params.keys(), args))
            bound.update(kwargs)
            value = bound.get(pname)
            if value is not None and not isinstance(value, Model):
                raise TypeError(
                    f"Parameter '{pname}' expected a Model instance, got {type(value).__name__}"
                )
        return fn(*args, **kwargs)

    return wrapper
