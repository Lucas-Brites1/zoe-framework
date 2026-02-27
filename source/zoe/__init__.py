

# Core
from zoe_application.application import App
from zoe_application.zoe_metadata import ZoeMetadata
from zoe_net.server import Server
def who_made_this():
    """Meet the dogs behind Zoe Framework 🐾"""
    App._easter_egg()

# Dependency Injection DI
from zoe_di.box import Box
from zoe_di.container import Container

# HTTP
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_http.code import HttpCode
from zoe_http.handler import Handler
from zoe_http.middleware import Middleware
from zoe_http.method import HttpMethod
from zoe_http.bytes import Bytes

# Router
from zoe_router.router import Router
from zoe_router.route import Route
from zoe_router.routes import Routes

# Schema
from zoe_schema.model_schema import Model
from zoe_schema.field_schema import Field

# Validators
from zoe_schema.schema_validators.not_null import NotNull
from zoe_schema.schema_validators.length import Length
from zoe_schema.schema_validators.range import Range
from zoe_schema.schema_validators.email import Email
from zoe_schema.schema_validators.pattern import Pattern
from zoe_schema.schema_validators.password import Password
from zoe_schema.schema_validators.max import Max
from zoe_schema.schema_validators.min import Min
from zoe_schema.schema_validators.one_of import OneOf

# Middlewares
from zoe_middlewares.logger import Logger
from zoe_middlewares.limiter import Limiter
from zoe_middlewares.cors import CORS
from zoe_middlewares.body_limiter import BodyLimiter
from zoe_middlewares.guard import Guard
from zoe_middlewares.guard_strategy import GuardStrategy, BearerStrategy, BasicStrategy, ApiKeyStrategy, AnyStrategy, AllStrategy

# Exceptions
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.http_exceptions.exc_not_found import RouteNotFoundException
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException

__all__ = [ # type: ignore
    # Utils
    "Bytes", "ZoeMetadata"
    # Core
    "App", "Server",
    # HTTP
    "Request", "Response", "HttpCode", "Handler", "Middleware", "HttpMethod", "Bytes"
    # Router
    "Router", "Route", "Routes",
    # Schema
    "Model", "Field",
    # GDependency Injection
    "Container", "Box",
    # Validators
    "NotNull", "Length", "Range", "Email", "Pattern",
    # Middlewares
    "Logger", "Limiter", "CORS", "BodyLimiter", "Guard", "GuardStrategy", "BearerStrategy",
    "BearerStrategy", "BasicStrategy", "ApiKeyStrategy", "AnyStrategy", "AllStrategy",
    # Exceptions
    "ZoeHttpException", "RouteNotFoundException", "InternalServerException",
    "ErrorCode", "ZoeSchemaAggregateException",
]
