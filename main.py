from source.zoe_net.server import Server
from source.zoe_application.application import Zoe
from source.zoe_router.router import Route, Routes, Router, Handler
from source.zoe_http import request, response,code,method
from source.zoe_middlewares.logger import Logger
from source.zoe_middlewares.limiter import Limiter

from source.zoe_schema.model_schema import Model

class Pessoa(Model):
    nome: str
    idade: int

class HelloHandler(Handler):
    def __call__(self: "HelloHandler", request: request.Request) -> response.Response:
        return response.Response(http_status_code=code.HttpCode.OK)

class PayloadHandler(Handler):
    def __call__(self: "PayloadHandler", request: request.Request, body: Pessoa) -> response.Response:
        print(request.query_params.id)
        return response.Response(code.HttpCode.CREATED, body={"user": body})

router: Router = Router(prefix="/teste")

if __name__ == "__main__":
    app: Zoe = Zoe(application_name="pi-api")
    router.add(route=Route(endpoint="/hello", method=method.HttpMethod.GET, handler=HelloHandler()))
    router.add(route=Route(endpoint="/user", method=method.HttpMethod.POST, handler=PayloadHandler()))
    app.include_router(router=router)

    app.use_middleware(middleware=Logger())
    app.use_middleware(middleware=Limiter(max_requests=2, window_seconds=10))
    server: Server = Server(application=app)
    server.run()            