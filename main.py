from source.zoe_net.server import Server
from source.zoe_application.application import Zoe
from source.zoe_router.router import Route, Router, Handler
from source.zoe_http import request, response,code,method
from source.zoe_middlewares.logger import Logger
from source.zoe_middlewares.limiter import Limiter

from source.zoe_schema.model_schema import Model, Field
from source.zoe_schema.schema_validators.length import Length

class Pessoa(Model):
    nome: str = Field(Length._min(n=4), Length._max(n=100))
    idade: int

class HelloHandler(Handler):
    def __call__(self: "HelloHandler", request: request.Request) -> response.Response:
        return response.Response(http_status_code=code.HttpCode.OK)

class PayloadHandler(Handler):
    def __call__(self: "PayloadHandler", request: request.Request, body: Pessoa) -> response.Response:
        print(request.path_params.user_id)
        print(request.path_params.user_password)
        return response.Response(code.HttpCode.CREATED, body={"user": body})

router: Router = Router(prefix="/teste")

if __name__ == "__main__":
    app: Zoe = Zoe(application_name="pi-api")
    router.POST(endpoint="/user/{user_id}", handler=PayloadHandler())
    app.use(router).use(Logger()).use(Limiter())
    
    server: Server = Server(application=app)
    server.run()            