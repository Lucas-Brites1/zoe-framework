from zoe_doc.doc_metadata import RouteInfo, DocMetadata
from zoe_http.handler import Handler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from zoe_router.router import Router

class DocRegistry:
  _routes_infos: list[RouteInfo] = []

  @classmethod
  def documentation_metadata(cls, handler: Handler) -> DocMetadata | None:
    return getattr(handler, "__zoe_doc__", None) or getattr(getattr(handler, "__zoe_original_handle__", None), "__zoe_doc__", None)

  @classmethod
  def from_router(cls, router: "Router") -> list[RouteInfo]:
    infos: list[RouteInfo] = []

    for route in router.assigned_routes.routes:
      doc_metadata: DocMetadata | None = cls.documentation_metadata(route.handler)
      if doc_metadata is None:
        continue

      infos.append(
        RouteInfo(
          method=route.method.value,
          handler=type(route.handler).__name__,
          path=route.endpoint,
          prefix=router.prefix,
          metadata=doc_metadata
        )
      )

    return infos

  @classmethod
  def all(cls) -> list[RouteInfo]:
    for route_info in cls._routes_infos:
      print(route_info)

    return cls._routes_infos
