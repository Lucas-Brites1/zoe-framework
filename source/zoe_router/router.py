from zoe_router.route import Route
from zoe_router.routes import Routes
from zoe_http.method import HttpMethod
from zoe_http.handler import Handler

class Router:
    def __init__(self: "Router", prefix: str) -> None:
        self.__assigned_routes: Routes = Routes()
        self.__prefix = prefix

    def add(self: "Router", route: Route) -> None:
        self.__assigned_routes.add(route=route)

    def resolve(self: "Router", method: HttpMethod, endpoint: str) -> Handler:
        for route in self.__assigned_routes:
            if route.method == method and route.endpoint == endpoint:
                return route.handler
        return None

    @property
    def assigned_routes(self: "Router") -> Routes:
        return self.__assigned_routes

    @property
    def prefix(self: "Router") -> str:
        return self.__prefix