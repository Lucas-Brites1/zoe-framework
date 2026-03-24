from zoe_router.route import Route
from zoe_doc.doc_registry import DocRegistry
from zoe_doc.doc_metadata import RouteInfo

class Routes:
    def __init__(self: "Routes") -> None:
        self.__routes_container: list[Route] = []

    @property
    def routes(self: "Routes") -> list[Route]:
        return self.__routes_container

    def add(self: "Routes", route: Route) -> "Routes":
      handler = route.handler
      doc_meta = (
          getattr(handler, "__zoe_doc__", None) or
          getattr(getattr(handler, "handle", None), "__zoe_doc__", None) or
          getattr(getattr(handler, "__zoe_original_handle__", None), "__zoe_doc__", None)
      )

      print(doc_meta)

      if doc_meta is not None:
          from zoe_doc.doc_registry import DocRegistry
          from zoe_doc.doc_metadata import RouteInfo
          DocRegistry.register(RouteInfo(
              method=route.method.value,
              path=route.endpoint,
              handler=type(handler).__name__,
              metadata=doc_meta
          ))

      self.__routes_container.append(route)
      return self

    def prioritize_static_routes(self: "Routes") -> None:
      static: list[Route] = []
      parametrized: list[Route] = []
      wildcard_routes: list[Route] = []

      for r in self.__routes_container:
        if r.endpoint.__contains__("{"):
            parametrized.append(r)
        elif r.endpoint.__contains__("/*"):
            wildcard_routes.append(r)
        else:
            static.append(r)

      self.__routes_container = static + parametrized + wildcard_routes

    def __iter__(self):
        return iter(self.__routes_container)

    @classmethod
    def from_routes(cls, routes: list[Route]) -> "Routes":
        if len(routes) == 0:
            raise Exception("Routes list cannot be empty")
        instance = cls()
        for route in routes:
            instance.add(route=route)
        return instance
