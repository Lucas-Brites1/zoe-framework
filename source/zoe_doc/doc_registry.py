from zoe_doc.doc_metadata import RouteInfo

class DocRegistry:
  _routes_infos: list[RouteInfo] = []

  @classmethod
  def register(cls, info: RouteInfo) -> None:
    cls._routes_infos.append(info)

  @classmethod
  def all(cls) -> list[RouteInfo]:
    return cls._routes_infos
