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
        params: list =  list(sig.parameters.values())
        if params and params[0].name == 'self':
            params = params[1:]

        format_signature: str = HandlerValidator._format_signature(func=func, sig=sig)

        if len(params) == 0:
             raise ZoeNonHttpError(
                exception_message=
                    f"Handler '{func.__name__}' must have at least one parameter (request: Request). "
                    f"Found signature: {format_signature}"
                )

        first_param = params[0]
        
        if first_param.annotation == Parameter.empty:
            raise ZoeNonHttpError(
                exception_message=(
                    f"Handler '{func.__name__}' first parameter must be typed as 'Request'.\n"
                    f"\tFound:    {format_signature}\n"
                    f"\t\tExpected: def {func.__name__}({first_param.name}: Request, ...) -> Response"
                )
            )

        first_param_type = getattr(first_param.annotation, '__name__', str(first_param.annotation))
        if first_param_type != 'Request':
            raise ZoeNonHttpError(
                exception_message=(
                    f"Handler '{func.__name__}' first parameter must be typed as 'Request'.\n"
                    f"\tFound:    {format_signature}\n"
                    f"\t\tExpected: def {func.__name__}({first_param.name}: Request, ...) -> Response"
                )
            )

        if sig.return_annotation != Signature.empty:
            return_type_name = getattr(sig.return_annotation, '__name__', str(sig.return_annotation))
            if return_type_name != 'Response':
                raise ZoeNonHttpError(
                    exception_message=(
                        f"Handler '{func.__name__}' must return 'Response'.\n"
                        f"\tFound return type: '{return_type_name}'. "
                        f"\t\tSignature: {format_signature}"
                    )
                )
        else:
            raise ZoeNonHttpError(
                exception_message=(
                    f"Handler '{func.__name__}' must have return type annotation '... -> Response'.\n"
                    f"\tFound: No return type specified.\n"
                    f"\t\tExpected signature:  def {func.__name__}(request: Request, ...) -> Response \n"
                    f"\t\tCurrent signature:   {format_signature}"
                )
            )

      