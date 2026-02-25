from zoe_http.handler import Handler
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_schema.model_schema import Model
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException
from zoe_schema.model_engine import ModelEngine
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException, HttpCode

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

      for param, class_reference in hints.items():
          if param in ("self", "request", "return"):
              continue
          if isinstance(class_reference, type) and Model.is_model(class_reference=class_reference):
                if request.body is None:
                    raise ZoeHttpException(
                        message=f"Request body is required but was not provided.",
                        status_code=HttpCode.BAD_REQUEST
                    )
                try:
                    #param == body
                    kwargs[param] = ModelEngine.validate_and_create(model_class=class_reference, data=request.body)
                except ZoeSchemaAggregateException as Zagexc:
                    return Zagexc.to_response(model_name=class_reference.__name__)
      return kwargs

  @staticmethod
  def invoke(handler: Handler, request: Request) -> Response:
    hints: dict = HandlerInvoker.get_hints(handler=handler)
    kwargs: dict = HandlerInvoker.resolve_kwargs(hints=hints, request=request)
    if isinstance(kwargs, Response):
      return kwargs
    return handler(request=request, **kwargs)
