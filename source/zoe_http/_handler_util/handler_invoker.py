#handler_invoker
from zoe_http.handler import Handler
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_schema.model_schema import Model
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException
from zoe_schema.model_engine import ModelEngine
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException, HttpCode
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_di.container import Container, Box
from zoe_di.inspector import Inspector
import typing
import inspect

class HandlerInvoker:
  @staticmethod
  def get_hints(handler: Handler) -> dict:
        return typing.get_type_hints(
            handler.handle,
            globalns=vars(inspect.getmodule(type(handler)))
        )

  @staticmethod
  def resolve_kwargs(hints: dict, request: Request) -> dict | Response:
    kwargs: dict = {}

    for param_name, class_reference in hints.items():
        if param_name in ("self", "request", "return"):
            continue

        #print(param) #<class 'zoe_http.request.Request'>
        #print(class_reference) #<class '__main__.UserRegister'>
        #print(f"Class<{class_reference}> é Model? {Model.is_model(class_reference)} - Parametro: {param}")

        if isinstance(class_reference, type) and Model.is_model(class_reference=class_reference):
            if not request.body.is_json():
                raise ZoeHttpException(
                        message={
                            "error": "Invalid request body",
                            "parameter": param_name,
                            "details": [
                                f"Expected: JSON object matching {param_name}",
                                f"Received: {request.headers.get('Content-Type', 'no Content-Type header')}",
                                f"The handler expects a JSON body to deserialize into '{param_name}'.",
                                "Make sure your request includes:",
                                "  - Header: Content-Type: application/json",
                                "  - Body: Valid JSON (e.g., {}, {'key': 'value'})"
                            ]
                        }
                    )

            if request.body.data is None or len(request.body.data) == 0:
                raise ZoeHttpException(
                    message=f"Request body is required but was not provided.",
                    status_code=HttpCode.BAD_REQUEST
                )
            try:
                kwargs[param_name] = ModelEngine.validate_and_create(model_class=class_reference, data=request.body.data) # type: ignore
            except ZoeSchemaAggregateException as Zagexc:
                return Zagexc.to_response(model_name=class_reference.__name__)
            continue

        class_ref_name: str = class_reference.__name__
        if Container.has(ref=param_name):
            kwargs[param_name] = Container.resolve(ref=param_name)
        elif Container.has(ref=class_reference.__name__):
            kwargs[param_name] = Container.resolve(ref=class_ref_name)

    return kwargs

  @staticmethod
  def invoke(handler: Handler, request: Request) -> Response:
    hints: dict = HandlerInvoker.get_hints(handler=handler)
    kwargs: dict = HandlerInvoker.resolve_kwargs(hints=hints, request=request) # type: ignore
    #kwargs could be a possible raised exception...    
    result = handler.handle(request=request, **kwargs)
    if result is None:
        handler_name: str = handler.__class__.__name__
        raise ZoeNonHttpError(
                exception_message=(
                    f"Handler '{handler_name}' returned None\n\n"
                    f"Problem:\n"
                    f"  The handle() method must return a Response object, but it returned None.\n"
                    f"  This usually means you forgot to add 'return' before Response.json().\n\n"
                    f"Fix:\n"
                    f"  class {handler_name}(Handler):\n"
                    f"      def handle(self, request: Request) -> Response:\n"
                    f"          return Response.json(...)  # <- Add 'return'!\n"
                )
            )
    if not isinstance(result, Response):
            handler_name = handler.__class__.__name__
            
            raise ZoeNonHttpError(
                exception_message=(
                    f"Handler '{handler_name}' returned invalid type\n\n"
                    f"Expected: Response\n"
                    f"Received: {type(result).__name__}\n\n"
                    f"Fix:\n"
                    f"  return Response.json(...)  # Must return Response object\n"
                )
            )
    return result