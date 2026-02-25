from zoe_http.handler import Handler
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_schema.model_schema import Model
from zoe_exceptions.schemas_exceptions import schema_unexpected_type, validation_exception
from zoe_exceptions import default_exception

import typing
import inspect

class HandlerInvoker:
  @staticmethod
  def get_hints(handler: Handler) -> dict:
      return typing.get_type_hints(
          handler.__call__,
          globalns=vars(inspect.getmodule(type(handler)))
      )

  @staticmethod
  def resolve_kwargs(hints: dict, request: Request) -> dict | Response:
      kwargs: dict = {}
      for param, class_reference in hints.items():
          if param in ("self", "request", "return"):
              continue
          if isinstance(class_reference, type) and Model.is_model(class_reference=class_reference):
              try:
                  body_instance = class_reference(**request.body)
                  kwargs[param] = body_instance
              except validation_exception.ValidatorException as exc:
                  return exc.to_response(model_name=class_reference.__name__)
              except schema_unexpected_type.SchemaFieldUnexpectedType as exc:
                  return exc.to_response(model_name=class_reference.__name__)
              except Exception as exc:
                  return default_exception.DefaultException(exception_message=str(exc)).to_response()
      return kwargs

  @staticmethod
  def invoke(handler: Handler, request: Request) -> Response:
    hints: dict = HandlerInvoker.get_hints(handler=handler)
    kwargs: dict = HandlerInvoker.resolve_kwargs(hints=hints, request=request)
    if isinstance(kwargs, Response):
      return kwargs
    return handler(request=request, **kwargs)
