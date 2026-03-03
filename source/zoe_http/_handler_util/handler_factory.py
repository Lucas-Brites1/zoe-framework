from inspect import Signature, signature
from zoe_http.handler import Handler
from zoe_http._handler_util.handler_validator import HandlerValidator
from typing import Callable, Any
from zoe_http.request import Request
from zoe_http.response import Response

class GenericHandlerFactory:
    __prefix_generic_handler: str = "Zoe_factory_generated_handler_"

    @staticmethod
    def __generate_handler_generic_name(fn: Callable) -> str:
        return GenericHandlerFactory.__prefix_generic_handler + fn.__name__

    @staticmethod
    def new(fn: Callable) -> Handler:
        HandlerValidator.validate_signature(func=fn)
        # 1. Validate the signature of the received function that will be wrapped inside the generated generic handler
        # 2. Generate Handler class with fixed prefix + random suffix to avoid conflicts between generated handlers
        # 3. Internally implement the Handler protocol signature: handle(self, request: Request, ...) -> Response
        # 4. When implementing the signature, also need to spread the kwargs that the dev's function may have
        # 5. Internally within the generated handle function, call the dev's function passing the expected parameters and return it
        # 6. Finally return the generated handler to the router
        handler_class_name: str = GenericHandlerFactory.__generate_handler_generic_name(fn=fn)
        sig: Signature = signature(obj=fn) # signature of the handle function declared by the dev
        params = list(sig.parameters) # parameters from the function signature

        def handle(self, request: Request, **kwargs: Any) -> Response:
            filtered_kwargs = {
                k: v for k, v in kwargs.items()
                if k in params
            }
            return fn(request, **filtered_kwargs)

        handle.__annotations__ = fn.__annotations__
        handler_generated: Handler = type( # type: ignore
            handler_class_name,
            (Handler, ),
            {
                'handle': handle
            }
        )
        return handler_generated() # type: ignore
