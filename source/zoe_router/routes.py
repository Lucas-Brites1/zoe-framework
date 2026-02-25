from zoe_router.route import Route

class Routes:
    def __init__(self: "Routes") -> None:
        self.__routes_container: list[Route] = []

    @property
    def routes(self: "Routes") -> list[Route]:
        return self.__routes_container

    def add(self: "Routes", route: Route) -> "Routes":
        self.__routes_container.append(route)
        return self

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
