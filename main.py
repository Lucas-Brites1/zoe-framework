from zoe_schema.model_schema import Model
from zoe_schema.field_schema import Field
from zoe_schema.schema_validators.length import Length
from zoe_schema.schema_validators.not_null import NotNull
from zoe_schema.schema_validators.range import Range
from zoe_schema.schema_validators.pattern import Pattern
from zoe_schema.schema_validators.email import Email
from zoe_application.application import Zoe
from zoe_router.router import Route, Router, Handler
from zoe_http import request, response, code
from zoe_middlewares.logger import Logger
from zoe_middlewares.limiter import Limiter
from zoe_net.server import Server

class Pessoa(Model):
    nome: str = Field(NotNull(), Length(max=10, min=5))
    idade: int = Field(NotNull(), Range(min=0, max=130))
    email: str = Field(NotNull(), Email())

class HelloHandler(Handler):
    def __call__(self: "HelloHandler", request: request.Request) -> response.Response:
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

    app.use(router_test).use(Logger(application_name="Project", verbose=False)).use(Limiter())

    server: Server = Server(application=app)
    server.run()
