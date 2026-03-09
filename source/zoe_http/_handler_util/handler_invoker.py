#handler_invoker
from zoe_http.handler import Handler
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_schema.model_schema import Model
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException
from zoe_schema.model_engine import ModelEngine
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException, HttpCode
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_exceptions.exc_handler_abort import HandlerAbortException
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
        if param_name in ("self", "return") or (isinstance(class_reference, type) and issubclass(class_reference, Request)):
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
              raise HandlerAbortException(Zagexc.to_response(model_name=class_reference.__name__))
            continue

        class_ref_name: str = class_reference.__name__
        if Container.has(ref=param_name):
            kwargs[param_name] = Container.resolve(ref=param_name)
        elif Container.has(ref=class_reference.__name__):
            kwargs[param_name] = Container.resolve(ref=class_ref_name)

        else:
          raise ZoeNonHttpError(
              why=f"Unresolved dependency '{param_name}: {class_reference.__name__}'",
              explain=(
                  f"The parameter '{param_name}' of type '{class_reference.__name__}' "
                  f"was not found in the container."
              ),
              fix=(
                  f"Register the dependency before starting the server:\n\n"
                  f"@Singleton(...) | @Transient(...) | @Scoped(...)\n"
                  f"class {class_reference.__name__}:\n"
                  f"    ...\n\n"
                  f"Or manually:\n"
                  f"Container.provide_instance('{param_name}', {class_reference.__name__}(...))"
              )
          )

    return kwargs

  @staticmethod
  def invoke(handler: Handler, request: Request) -> Response:
    hints: dict = HandlerInvoker.get_hints(handler=handler)

    request_param_name = "request"
    for param_name, class_reference in hints.items():
        if isinstance(class_reference, type) and issubclass(class_reference, Request):
            request_param_name = param_name
            break

    Container._open_scope()
    try:
        try:
            kwargs: dict = HandlerInvoker.resolve_kwargs(hints=hints, request=request) # type: ignore
        except HandlerAbortException as abort:
            return abort.response
        except ZoeNonHttpError as e:
            raise e

        result = handler.handle(**{request_param_name: request}, **kwargs)
        if result is None:
            handler_name: str = handler.__class__.__name__
            raise ZoeNonHttpError(
                    why=f"Handler '{handler_name}' returned None",
                    explain=(
                        f"The handle() method must return a Response object, but it returned None.\n"
                        f"This usually means you forgot to add 'return' before Response.type_of_response()."
                    ),
                    fix=(
                        f"class {handler_name}(Handler):\n"
                        f"    def handle(self, request: Request) -> Response:\n"
                        f"        return Response.type_of_response(...)  # <- Add 'return'!"
                    )
                )
        if not isinstance(result, Response):
                handler_name = handler.__class__.__name__

                raise ZoeNonHttpError(
                    why=f"Handler '{handler_name}' returned invalid type",
                    explain=(
                        f"Expected: Response\n"
                        f"Received: {type(result).__name__}"
                    ),
                    fix=f"return Response.json(...)  # Must return Response object"
                )
        return result
    finally:
      Container._close_scope()

