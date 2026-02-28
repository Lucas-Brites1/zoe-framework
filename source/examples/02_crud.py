# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 02 — Basic CRUD
# ─────────────────────────────────────────────────────────────────────────────
#
# Now that you know how to spin up a server, let's build something real.
# In this example we'll create a simple user registration endpoint.
#
# New concepts introduced here:
#   - Model    — defines the shape of your request body
#   - Router   — groups related routes under a shared prefix
#   - Body injection — Zoe automatically parses and injects the request body
#
# Note: we are intentionally NOT using validators (Field, NotNull, Email...) yet.
# That comes in the next example. Baby steps. :)
# ─────────────────────────────────────────────────────────────────────────────

from zoe import (
    App,      # The application container — registers routes, routers and middlewares.
    Server,   # Opens the socket and starts listening for HTTP connections.
    Router,   # Groups routes under a shared URL prefix. Here we'll use "/users".
    Handler,  # Base class for request handlers. Implement handle() to process requests.
    Response, # Wraps your data and HTTP status into a valid HTTP response.
    HttpCode, # Enum with standard HTTP status codes — 200, 201, 404, 500...
    Model,    # Base class for request body schemas. Define your fields as type annotations.
    Logger,   # Logs every request with method, path, status code and response time.
)

# ─────────────────────────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────────────────────────
#
# A Model defines the expected shape of a request body.
# You declare fields as type annotations — just like a regular Python class.
#
# Zoe reads these annotations and automatically:
#   1. Parses the incoming JSON body
#   2. Creates an instance of the Model
#   3. Injects it into your handle() method
#
# No manual request.json() or body parsing needed.
#
from zoe import Assert, Field
class UserRegisterModel(Model):
    login: str = Field(Assert(expected_value="lucas"))
    password: str
    email: str
    role: str

class UserModel(Model):
    user: UserRegisterModel
    user_id: int

# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY DATABASE
# ─────────────────────────────────────────────────────────────────────────────
#
# We'll simulate a database using a plain Python dict.
# Each user gets an auto-incremented integer ID starting from 1.
# This ID will be useful later for fetching, updating and deleting users.
#
_users: dict[int, UserModel] = {}

# ─────────────────────────────────────────────────────────────────────────────
# HANDLERS
# ─────────────────────────────────────────────────────────────────────────────

class RegisterHandler(Handler):
    def handle(self, body: UserRegisterModel) -> Response:
        # Notice the `body: UserRegisterModel` parameter.
        # You don't need to parse the request manually — Zoe sees that type hint,
        # parses the incoming JSON and injects a UserRegisterModel instance here.
        # If the body is missing or malformed, Zoe returns 400 automatically.

        new_id: int = len(_users) + 1  # IDs start at 1
        new_user: UserModel = UserModel(user=body, user_id=new_id)
        _users[new_id] = new_user

        return Response(
            http_status_code=HttpCode.CREATED,  # 201 — resource created successfully
            body={
                "message": f"Account for {body.email} created successfully!",
                "data": new_user  # Zoe serializes the Model instance automatically
            }
        )

class ListUsersHandler(Handler):
    def handle(self) -> Response:
        # No body injection needed here — we're just reading from our "database".
        return Response(
            http_status_code=HttpCode.OK,
            body={
                "users": list(_users.values()),
                "total": len(_users)
            }
        )

class GetUserHandler(Handler):
    def handle(self) -> Response:
        # Path params are accessible via self.request.path_params
        # Since the route is "/users/{user_id}", Zoe extracts {user_id} automatically.
        user_id: int = int(self.request.path_params.user_id)
        user: UserModel | None = _users.get(user_id, None)

        if not user:
            return Response(
                http_status_code=HttpCode.NOT_FOUND,
                body={"error": f"User with id {user_id} not found."}
            )

        return Response(http_status_code=HttpCode.OK, body={"data": user})

class DeleteUserHandler(Handler):
    def handle(self) -> Response:
        user_id: int = int(self.request.path_params.user_id)

        if user_id not in _users:
            return Response(
                http_status_code=HttpCode.NOT_FOUND,
                body={"error": f"User with id {user_id} not found."}
            )

        del _users[user_id]
        return Response(http_status_code=HttpCode.NO_CONTENT)  # 204 — deleted, no body

# ─────────────────────────────────────────────────────────────────────────────
# WIRING IT ALL TOGETHER
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app: App = App()
    server: Server = Server(application=app)

    # Router groups all user-related routes under the "/users" prefix.
    # This means:
    #   .POST("/")           → POST /users/
    #   .GET("/")            → GET  /users/
    #   .GET("/{user_id}")   → GET  /users/{user_id}
    #   .DELETE("/{user_id}")→ DELETE /users/{user_id}
    from zoe import Guard, BearerStrategy
    user_router: Router = Router(prefix="/users")
    user_router \
        .POST("/", RegisterHandler())        \
        .GET("/", ListUsersHandler())        \
        .GET("/{user_id}", GetUserHandler()) \
        .DELETE("/{user_id}", DeleteUserHandler())

    from zoe import Limiter, Guard, BearerStrategy, BodyLimiter, Bytes
    app.use(user_router).use(Logger(application_name="My-App", verbose=False))

    # Try these requests:
    #   POST   http://127.0.0.1:7777/users/      request_body: {"login": "lucas", "password": "123", "email": "lucas@zoe.dev"}
    #   GET    http://127.0.0.1:7777/users/
    #   GET    http://127.0.0.1:7777/users/1
    #   DELETE http://127.0.0.1:7777/users/1
    server.run()

