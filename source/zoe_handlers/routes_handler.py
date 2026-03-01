from zoe_http.handler import Handler
from zoe_http.response import Response
from zoe_http.request import Request
from zoe_http.code import HttpCode
from zoe_router.router import Router
from zoe_router.route import Route
from zoe_application.zoe_metadata import ZoeMetadata

class RoutesHandler(Handler):
    def __init__(self: "RoutesHandler", routers: list[Router]):
        self.routers = routers

    @staticmethod
    def get_handler(routers: list[Router]) -> Route:
        return Route.get(endpoint="/routes", handler=RoutesHandler(routers))

    @staticmethod
    def __serialize_router(router: Router) -> dict:
        return {
            "prefix": router.prefix,
            "routes": [
                {
                    "method": route.method.value,
                    "endpoint": RoutesHandler.__normalize(router.prefix + route.endpoint),
                    "handler": route.handler.__class__.__name__
                }
                for route in router.assigned_routes
            ]
        }

    @staticmethod
    def __normalize(endpoint: str) -> str:
        if len(endpoint) > 1 and endpoint.endswith("/"):
            return endpoint[:-1]
        return endpoint

    def handle(self: "RoutesHandler", request: Request) -> Response:
        if not ZoeMetadata.is_debug():
            return Response.json(
                http_code=HttpCode.NOT_FOUND,
                body={"error": "Not available outside debug mode."}
                )

        return Response.json(
            http_code=HttpCode.OK,
            body={
                "base-router": self.__serialize_router(self.routers[0]),
                "api-routers": [self.__serialize_router(r) for r in self.routers[1:]]
            }
        )
