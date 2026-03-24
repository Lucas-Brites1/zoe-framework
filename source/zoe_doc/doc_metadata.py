from typing import Any, Type, Optional, TypedDict, Required, NotRequired
from zoe_schema.model_schema import Model
from zoe_di.lifecycle import Lifecycle
from enum import Enum

class Summary(TypedDict):
  title:        Required[str]
  description:  NotRequired[str]
  tags:         NotRequired[list[str]]

class Author(TypedDict):
  name:     Required[str]
  email:    NotRequired[str]
  squad:    NotRequired[str]
  team:     NotRequired[str]
  contact:  NotRequired[str | list[str]]

class RouteParam(TypedDict):
  name:   Required[str]
  reason: Required[str]

class RouteHeader(TypedDict):
  header_key:   Required[str]
  header_value: Required[str]
  reason:       NotRequired[str]

class RouteRequest(TypedDict):
  query_params: NotRequired[list[RouteParam]]
  path_params:  NotRequired[list[RouteParam]]
  headers:      NotRequired[list[RouteHeader]]
  body:         NotRequired[Type[Model]]
  examples:     NotRequired[dict[str, dict[str, Any]]]

class RouteResponse(TypedDict):
  status_code: Required[int]
  description: Required[str]
  body:        NotRequired[Type[Model]]
  examples:     NotRequired[dict[str, dict[str, Any]]]

class DocAuthScheme(Enum):
  BEARER = "bearer"
  APIKEY = "apikey"
  BASIC  = "basic"
  OAUTH2 = "oauth2"

class RouteSecurity(TypedDict):
  scheme: Required[DocAuthScheme | str]
  description: NotRequired[str]

class DependsOn(TypedDict):
  service:    Required[str]
  reason:     NotRequired[str]
  lifecycle:  NotRequired[Lifecycle]

class LogicStep(TypedDict):
    what:  Required[str]
    how:   NotRequired[str]
    why:   NotRequired[str]

class BusinessLogic(TypedDict):
  summary:  Required[str]
  steps:    NotRequired[list[LogicStep]]
  notes:    NotRequired[str]

class DocMetadata(TypedDict):
    summary:      NotRequired[Summary]
    author:       NotRequired[Author]
    request:      NotRequired[RouteRequest]
    responses:    NotRequired[list[RouteResponse]]
    security:     NotRequired[RouteSecurity]
    logic:        NotRequired[BusinessLogic]
    depends_on:   NotRequired[list[DependsOn]]
    deprecated:   NotRequired[bool]
    version:      NotRequired[str]

class RouteInfo(TypedDict):
  method:   str
  path:     str
  prefix:   str # from router
  handler:  str
  metadata: DocMetadata
