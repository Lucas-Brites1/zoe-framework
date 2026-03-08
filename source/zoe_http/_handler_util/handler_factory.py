from inspect import Signature, signature
from zoe_http.handler import Handler
from zoe_http._handler_util.handler_validator import HandlerValidator
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_internal_exc import InternalServerException
from typing import Callable, Any
from zoe_http.request import Request
from zoe_http.response import Response
import sys

class GenericHandlerFactory:
    __prefix_generic_handler: str = "Zoe_factory_generated_handler_"

    @staticmethod
    def __generate_handler_generic_name(fn: Callable) -> str:
        return GenericHandlerFactory.__prefix_generic_handler + fn.__name__

    @staticmethod
    def new(fn: Callable) -> Handler:
        try:
            HandlerValidator.validate_signature(func=fn)
        except ZoeNonHttpError as e:
            InternalServerException.from_non_http_error(error=e, request=None)
            sys.exit(1)

        handler_class_name: str = GenericHandlerFactory.__generate_handler_generic_name(fn=fn)
        sig: Signature = signature(obj=fn)
        params = list(sig.parameters)

        def handle(self, request: Request, **kwargs: Any) -> Response:
            filtered_kwargs = {
                k: v for k, v in kwargs.items()
                if k in params
            }
            return fn(request, **filtered_kwargs)

        handle.__annotations__ = fn.__annotations__
        handler_generated: Handler = type(  # type: ignore
            handler_class_name,
            (Handler,),
            {'handle': handle}
        )
        return handler_generated()  # type: ignore
