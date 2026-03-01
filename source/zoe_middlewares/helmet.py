from zoe_http.response import Response
from zoe_http.request import Request
from typing import Callable
from enum import Enum

class HelmetCrossOriginEmbedderPolicy(Enum):
  REQUIRE_CORP = "require-corp"
  UNSAFE_NONE = "unsafe-none"

class HelmetPermissionsPolicy(Enum):
  CAMERA = "camera=()"
  MICROPHONE = "microphone=()"
  GEOLOCATION = "geolocation=()"
  PAYMENT = "payment=()"

class Helmet:
  __DEFAULT_HEADERS: dict[str, str] = {
      "Content-Security-Policy":        "default-src 'self';base-uri 'self';font-src 'self' https: data:;form-action 'self';frame-ancestors 'self';img-src 'self' data:;object-src 'none';script-src 'self';script-src-attr 'none';style-src 'self' https: 'unsafe-inline';upgrade-insecure-requests",
      "Cross-Origin-Opener-Policy":     "same-origin",
      "Cross-Origin-Resource-Policy":   "same-origin",
      "Origin-Agent-Cluster":           "?1",
      "Referrer-Policy":                "no-referrer",
      "Strict-Transport-Security":      "max-age=15552000; includeSubDomains",
      "X-Content-Type-Options":         "nosniff",
      "X-DNS-Prefetch-Control":         "off",
      "X-Download-Options":             "noopen",
      "X-Frame-Options":                "SAMEORIGIN",
      "X-Permitted-Cross-Domain-Policies": "none",
      "X-XSS-Protection":               "0",
  }

  def __init__(
      self: "Helmet",
      permissions_policy: list[HelmetPermissionsPolicy] | None = None,
      cross_origin_embedder_policy: HelmetCrossOriginEmbedderPolicy | None = None,
      hsts: bool = True
    ):
    self.permissions_policy = permissions_policy
    self.cross_origin_embedder_policy = cross_origin_embedder_policy
    self.__hsts = hsts

  def __insert_headers(self: "Helmet", response: Response) -> Response:
    for header_name, header_value in self.__DEFAULT_HEADERS.items():
      if header_name == "Strict-Transport-Security" and not self.__hsts:
        continue
      response.add_header(header_name, header_value)

    if self.permissions_policy:
      value = ", ".join([p.value for p in self.permissions_policy])
      response.add_header("Permissions-Policy", value)

    if self.cross_origin_embedder_policy:
      response.add_header("Cross-Origin-Embedder-Policy", self.cross_origin_embedder_policy.value)

    return response

  def process(self: "Helmet", request: Request, next: Callable) -> Response:
    response = next(request)
    return self.__insert_headers(response=response)
