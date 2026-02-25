from source.zoe_net.server import Server
from source.zoe_application.application import Zoe
from source.zoe_router.router import Route, Router, Handler
from source.zoe_http import request, response,code
from source.zoe_middlewares.logger import Logger
from source.zoe_middlewares.limiter import Limiter

from source.zoe_schema.model_schema import Model
from source.zoe_schema.field_schema import Field
from source.zoe_schema.schema_validators.length import Length
from source.zoe_schema.schema_validators.not_null import NotNull
from source.zoe_schema.schema_validators.range import Range
from source.zoe_schema.schema_validators.pattern import Pattern
from source.zoe_schema.schema_validators.email import Email

class Pessoa(Model):
    nome: str = Field(NotNull(), Length(max=10))
    idade: int = Field(NotNull(), Range(min=0, max=130))
    email: str = Field(NotNull(), Email())

class HelloHandler(Handler):
    def __call__(self: "HelloHandler", request: request.Request) -> response.Response:
        print(request.query_params.message)
        return response.Response(http_status_code=code.HttpCode.OK)

class PayloadHandler(Handler):
    def __call__(self: "PayloadHandler", request: request.Request, body: Pessoa) -> response.Response:
        print(request.path_params.user_id)
        return response.Response(code.HttpCode.CREATED, body={"user": body})

router_test: Router = Router(prefix="/teste")

if __name__ == "__main__":
    app: Zoe = Zoe()

    router_test\
      .POST(endpoint="/user/{user_id}", handler=PayloadHandler())\
      .GET(endpoint="/hello", handler=HelloHandler())

    app.use(router_test).use(Logger()).use(Limiter())

    server: Server = Server(application=app)
    server.run()
