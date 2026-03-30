from zoe_error_handler.error_handler_protocol import ErrorHandler
from zoe_exceptions.http_exceptions.exc_domain import DomainException
from zoe_error_handler.registry import DomainErrorDispatcher
from zoe_di.inspector import Inspector, CallableInfo, ParamInfo
from zoe_exceptions.exc_internal_exc import InternalServerException, ZoeNonHttpError
from zoe_http.request import Request
from zoe_http.response import Response
from typing import Callable

def on_error(domain_exception: type[DomainException]):
    def wrapped_handle(callable: Callable) -> Callable:
        _verify_error_handler_signature(callable)
        DomainErrorDispatcher .register(domain_exception, callable)
        return callable
    return wrapped_handle

def _verify_error_handler_signature(callable: Callable) -> None:
    infos: CallableInfo = Inspector.callable_infos(callable)
    params = infos.callable_params  # dict[str, ParamInfo]

    if len(params) < 2:
        raise InternalServerException.from_non_http_error(
            ZoeNonHttpError(
                why=f"@on_error handler '{infos.callable_name}' has wrong signature",
                explain=(
                    f"Expected 2 parameters: (exception: DomainException, request: Request)\n"
                    f"Got {len(params)} parameter(s) instead."
                ),
                fix="async def handle(exception: MyError, request: Request) -> Response: ..."
            )
        )

    first = list(params.values())[0]
    if not (isinstance(first.param_type, type) and issubclass(first.param_type, DomainException)):
        raise InternalServerException.from_non_http_error(
            ZoeNonHttpError(
                why=f"@on_error handler '{infos.callable_name}' first parameter must be a DomainException subclass",
                explain=(
                    f"Got '{first.param_type}' instead.\n"
                    f"The first parameter must be the exception being handled."
                ),
                fix="async def handle(exc: MyError, req: Request) -> Response: ..."
            )
        )

    second = list(params.values())[1]
    if second.param_type is not Request:
        raise InternalServerException.from_non_http_error(
            ZoeNonHttpError(
                why=f"@on_error handler '{infos.callable_name}' second parameter must be Request",
                explain=f"Got '{second.param_type}' instead.",
                fix="async def handle(exc: MyError, req: Request) -> Response: ..."
            )
        )

    if infos.callable_return_type is not Response:
        raise InternalServerException.from_non_http_error(
            ZoeNonHttpError(
                why=f"@on_error handler '{infos.callable_name}' must return Response",
                explain=f"Got '{infos.callable_return_type}' instead.",
                fix="async def handle(exc: MyError, req: Request) -> Response: ..."
            )
        )
