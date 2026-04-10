# Core
from zoe_application.application import App
from zoe_application.zoe_metadata import Zoe, Config
from zoe_net.server import Server


def who_made_this():
    """Meet the dogs behind Zoe Framework 🐾"""
    App._easter_egg()


# Dependency Injection
from pathlib import Path

# Cache
from zoe_cache.decorators.cache import cache
from zoe_cache.decorators.invalidates import invalidates

# DI
from zoe_di.auto_inject import Injectable
from zoe_di.box import Box
from zoe_di.container import Container
from zoe_di.lifecycle import Lifecycle
from zoe_di.scoped import Scoped
from zoe_di.singleton import Singleton
from zoe_di.transient import Transient
from zoe_doc.doc_generator import doc

# Documentation
from zoe_doc.doc_metadata import *

# Environment
from zoe_env.env import Env

# Errors
from zoe_error_handler.error_handler_protocol import ErrorHandler
from zoe_error_handler.on_error import on_error
from zoe_exceptions.exc_handler_abort import HandlerAbortException
from zoe_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.http_exceptions.exc_domain import DomainException

# Exceptions
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.http_exceptions.exc_not_allowed import MethodNotAllowedException
from zoe_exceptions.http_exceptions.exc_not_found import RouteNotFoundException
from zoe_exceptions.http_exceptions.exc_resource_not_found import NotFoundException
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException
from zoe_exceptions.schemas_exceptions.exc_base import ErrorCode

# File Utils
from zoe_http._file_util import FileUtil
from zoe_http._request_util.request_auth import Auth
from zoe_http._request_util.request_multipart import Multipart

# Upload
from zoe_http._request_util.upload_file import UploadFile
from zoe_http._response_util._pagination import Filter

# HTTP-Utils
from zoe_http._response_util.response_cookies import (
    CookieAttributes,
    CookiePair,
    ResponseCookie,
    SameSitePolicy,
)
from zoe_http.bytes import Bytes
from zoe_http.code import HttpCode
from zoe_http.handler import Handler
from zoe_http.hooks import Hook
from zoe_http.method import HttpMethod
from zoe_http.middleware import Middleware
from zoe_http.middleware_async import AsyncMiddleware

# HTTP
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_jwt.jwt_exceptions import (
    ExpiredTokenError,
    InvalidAlgorithmError,
    InvalidSignatureError,
    InvalidTokenError,
    JWTError,
    TokenNotYetValidError,
)

# Auth
from zoe_jwt.jwt_hs256 import JWT_HS256, JWT_Claim
from zoe_jwt.token_validator import TokenValidator

# Logging
from zoe_log.decorators import loggable, subloggable
from zoe_log.log import Log
from zoe_log.loglevel import LogLevel
from zoe_middlewares.body_limiter import BodyLimiter
from zoe_middlewares.cors import CORS
from zoe_middlewares.guard import Guard
from zoe_middlewares.guard_strategy import (
    AllStrategy,
    AnyStrategy,
    ApiKeyStrategy,
    BasicStrategy,
    BearerStrategy,
    GuardStrategy,
)
from zoe_middlewares.helmet import (
    Helmet,
    HelmetCrossOriginEmbedderPolicy,
    HelmetPermissionsPolicy,
)
from zoe_middlewares.limiter import Limiter

# Middlewares
from zoe_middlewares.logger import Logger
from zoe_middlewares.static_files import StaticFiles
from zoe_router.route import Route

# Router
from zoe_router.router import Router
from zoe_router.routes import Routes

# Schema Classes Related
from zoe_schema.computed_field_schema import ComputedField
from zoe_schema.decorators import ensure_model
from zoe_schema.field_schema import Field

# Generators
from zoe_schema.field_schema_generator import FieldGenerator  # base class

# Validators
from zoe_schema.field_schema_validator import FieldValidator  # base class

# Schema
from zoe_schema.model_schema import Model, Strict
from zoe_schema.schema_generators.date_generator import Date, DateFormat
from zoe_schema.schema_generators.slug_generator import Slug
from zoe_schema.schema_generators.token_generator import Token
from zoe_schema.schema_generators.uuid_generator import UUID
from zoe_schema.schema_validators.assert_validator import Assert
from zoe_schema.schema_validators.email import Email
from zoe_schema.schema_validators.max import Max
from zoe_schema.schema_validators.min import Min
from zoe_schema.schema_validators.not_null import NotNull
from zoe_schema.schema_validators.one_of import OneOf
from zoe_schema.schema_validators.password import Password
from zoe_schema.schema_validators.pattern import Pattern
from zoe_schema.schema_validators.range import Range
from zoe_schema.schema_validators.required import Required


def reset_container() -> None:
    Container.reset()


def reset_cache() -> None:
    from zoe_cache.cache_registry import CacheRegistry

    CacheRegistry.clear()


__all__ = [  # type: ignore
    # Utils
    "Bytes",
    "Zoe",
    "Config",
    "Env",
    "FileUtil",
    "Path",
    # Core
    "App",
    "Server",
    # HTTP
    "Request",
    "Response",
    "HttpCode",
    "Handler",
    "Middleware",
    "AsyncMiddleware",
    "HttpMethod",
    "Hook",
    # HTTP-UTILS
    "SameSitePolicy",
    "CookieAttributes",
    "CookiePair",
    "Filter",
    "ResponseCookie",
    # Upload
    "UploadFile",
    "Multipart",
    "Auth",
    # Router
    "Router",
    "Route",
    "Routes",
    # Schema
    "Model",
    "Field",
    "Strict",
    "ComputedField",
    "ensure_model",
    # Dependency Injection
    "Container",
    "Box",
    "Singleton",
    "Transient",
    "Scoped",
    "Injectable",
    "Lifecycle",
    # Validators
    "FieldValidator",
    "NotNull",
    "Range",
    "Email",
    "Pattern",
    "Password",
    "Min",
    "Max",
    "OneOf",
    "Assert",
    "Required",
    # Generators
    "FieldGenerator",
    "Date",
    "DateFormat",
    "UUID",
    "Token",
    "Slug",
    # Auth
    "JWT_HS256",
    "TokenValidator",
    "JWT_Claim",
    # Loggin
    "Log",
    "LogLevel",
    "loggable",
    "subloggable",
    # Middlewares
    "Logger",
    "Limiter",
    "CORS",
    "BodyLimiter",
    "Guard",
    "GuardStrategy",
    "BearerStrategy",
    "BasicStrategy",
    "ApiKeyStrategy",
    "AnyStrategy",
    "AllStrategy",
    "Helmet",
    "HelmetCrossOriginEmbedderPolicy",
    "HelmetPermissionsPolicy",
    "StaticFiles",
    # Errors Handler
    "ErrorHandler",
    "on_error",
    # Exceptions
    "ZoeHttpException",
    "DomainException",
    "RouteNotFoundException",
    "MethodNotAllowedException",
    "NotFoundException",
    "InternalServerException",
    "HandlerAbortException",
    "ErrorCode",
    "ZoeSchemaAggregateException",
    "JWTError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "InvalidAlgorithmError",
    "InvalidSignatureError",
    "TokenNotYetValidError",
    # Cache
    "invalidates",
    "cache",
    # Documentation
    "doc",
    "DocMetadata",
    "Summary",
    "Author",
    "RouteParam",
    "RouteHeader",
    "RouteRequest",
    "RouteResponse",
    "RouteSecurity",
    "DocAuthScheme",
    "DependsOn",
    "LogicStep",
    "BusinessLogic",
]
