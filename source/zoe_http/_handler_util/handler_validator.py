from typing import Callable, get_type_hints
from inspect import signature, isfunction, ismethod, isclass, Signature, Parameter
from zoe_http.response import Response
from zoe_http.request import Request
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError


class HandlerValidator:
    @staticmethod
    def _format_signature(func: Callable, sig: Signature) -> str:
        params_str = []
        for param_name, param in sig.parameters.items():
            if param.annotation == Parameter.empty:
                params_str.append(param_name)
            else:
                type_name = getattr(param.annotation, '__name__', str(param.annotation))
                params_str.append(f"{param_name}: {type_name}")

        if sig.return_annotation == Signature.empty:
            return_str = "-> None"
        else:
            return_type = getattr(sig.return_annotation, '__name__', str(sig.return_annotation))
            return_str = f" -> {return_type}"

        return f"def {func.__name__}({', '.join(params_str)}){return_str}"

    @staticmethod
    def validate_signature(func: Callable) -> None:
        sig: Signature = signature(obj=func)
        params: list = list(sig.parameters.values())
        if params and params[0].name == 'self':
            params = params[1:]

        format_signature: str = HandlerValidator._format_signature(func=func, sig=sig)

        if len(params) == 0:
            raise ZoeNonHttpError(
                why=f"Handler '{func.__name__}' has no parameters",
                explain=(
                    f"Every handler must accept at least a Request as first parameter.\n"
                    f"Found: {format_signature}"
                ),
                fix=(
                    f"def {func.__name__}(request: Request) -> Response:\n"
                    f"    ..."
                )
            )

        first_param = params[0]

        if first_param.annotation == Parameter.empty:
            raise ZoeNonHttpError(
                why=f"Handler '{func.__name__}' first parameter has no type annotation",
                explain=(
                    f"The first parameter must be explicitly typed as 'Request'.\n"
                    f"Found: {format_signature}"
                ),
                fix=(
                    f"def {func.__name__}(request: Request....) -> Response:\n"
                    f"    ..."
                )
            )

        first_param_type = getattr(first_param.annotation, '__name__', str(first_param.annotation))
        if first_param_type != 'Request':
            raise ZoeNonHttpError(
                why=f"Handler '{func.__name__}' first parameter type is not 'Request'",
                explain=(
                    f"The first parameter must be typed as 'Request', not '{first_param_type}'.\n"
                    f"Found: {format_signature}"
                ),
                fix=(
                    f"def {func.__name__}(request: Request...) -> Response:\n"
                    f"    ..."
                )
            )

        if sig.return_annotation == Signature.empty:
            raise ZoeNonHttpError(
                why=f"Handler '{func.__name__}' has no return type annotation",
                explain=(
                    f"Handlers must explicitly declare '-> Response' as return type.\n"
                    f"Found: {format_signature}"
                ),
                fix=(
                    f"def {func.__name__}(request: Request...) -> Response:\n"
                    f"    ..."
                )
            )

        return_type_name = getattr(sig.return_annotation, '__name__', str(sig.return_annotation))
        if return_type_name != 'Response':
            raise ZoeNonHttpError(
                why=f"Handler '{func.__name__}' return type is not 'Response'",
                explain=(
                    f"Expected return type 'Response', found '{return_type_name}'.\n"
                    f"Found: {format_signature}"
                ),
                fix=(
                    f"def {func.__name__}(request: Request...) -> Response:\n"
                    f"    ..."
                )
            )
