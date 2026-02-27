from zoe_http.request import Request
from zoe_http.response import Response
from zoe_router.router import Router
from zoe_http.handler import Handler
from zoe_router.router import Route, Routes, Router
from zoe_http.middleware import Middleware
from zoe_application.handler_invoker import HandlerInvoker
from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.http_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.http_exceptions.exc_not_found import RouteNotFoundException

class App:
    def __init__(self: "App") -> None:
        self.__base_router: Router = Router(prefix="")
        self.__routers: list[Router] = [self.__base_router]
        self.__middlewares: list[Middleware] = []

    def use(self: "App", to_add: Route | Routes | Router | Middleware) -> "App":
        match type(to_add).__name__:
            case "Route":
                self.__base_router.add(route=to_add) # type: ignore
            case "Routes":
                for route in to_add: # type: ignore
                    self.__base_router.add(route=route)
            case "Router":
                self.__routers.append(to_add) # type: ignore
            case "Middleware":
                self.__middlewares.append(to_add) # type: ignore
            case _:
                if hasattr(to_add, '__call__') and not isinstance(to_add, (Route, Routes, Router)):
                    self.__middlewares.append(to_add)
                else:
                    raise TypeError(f"Cannot register type '{type(to_add).__name__}'")
        return self

    def _resolve(self, request: Request) -> Response:
        def call_handler(req: Request) -> Response:
            for router in self.__routers:
                response = router.resolve(method=req.method, endpoint=req.route, request=request)
                if response is not None:
                  return response
            return RouteNotFoundException(request=request).to_response()

        chain = call_handler
        for middleware in reversed(self.__middlewares):
            previous = chain
            def chain(req, m=middleware, p=previous):
                return m(req, p)

        try:
            return chain(request)
        except ZoeHttpException as exc:
            return exc.to_response()
        except Exception as exc:
            return InternalServerException(detail=str(exc)).to_response()

    @staticmethod
    def _easter_egg() -> None:
        # I don't have a favorite — all three are equally loved.
        # I named this framework "Zoe" because she was the first,
        # but my goal is to build a meaningful project named after each of my dogs
        # as a way to honor them and keep their names alive in something I've created.
        # Mayla and Clara, your time will come.
        this_year: int = 2026
        my_dogs: dict[str, object] = {
            "Zoe": {
                "current-age": "5 years",
                "breed": "Golden Retriever",
                "likes": "to play with toys and take a nap",
                "fun-fact": "the framework was named after her 🐾"
            },
            "Mayla": {
                "current-age": "4 years",
                "breed": "Golden Retriever",
                "likes": "to walk and take a nap"
            },
            "Clara": {
                "current-age": "2 years",
                "breed": "Dachshund",
                "likes": "obsessed with playing fetch"
            }
        }

        print("\033[93m")
        print("  🐾 The dogs behind Zoe Framework:\n")
        for name, info in my_dogs.items():
            print(f"  {name}")
            for k, v in info.items():
                print(f"    {k}: {v}")
            print()
        print(f"  All healthy and happy in {this_year} 🧡")
        print("\033[0m")
