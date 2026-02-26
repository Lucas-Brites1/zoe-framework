# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 01 — Hello, World!
# ─────────────────────────────────────────────────────────────────────────────
#
# If you are completely new to web servers and APIs, this example is for you!
# We'll walk through every single concept step by step — no shortcuts.
# Already know the basics? No worries, jump straight to the next examples. :)
#
# Let's get started!
# ─────────────────────────────────────────────────────────────────────────────

from zoe import (
    App,      # The core of your application. Think of it as the "brain" —
              # everything gets registered here: routes, routers and middlewares.

    Server,   # This is what actually opens a socket and listens for connections.
              # It handles all the low-level TCP and HTTP protocol stuff so you don't have to.
              # Call .run() when you're ready to start serving requests.

    Router,   # A Router groups related routes under a shared URL prefix.
              # For example: Router("/users") groups /users, /users/{id}, /users/{id}/posts...
              # Think of it as a folder for your routes.

    Route,    # A Route is a single endpoint — a URL + HTTP method + a Handler.
              # You can add it directly to App or nest it inside a Router.

    Handler,  # This is the base class that every request handler must extend.
              # It works like an interface — it forces you to implement handle()
              # which is the function that actually processes the incoming request.

    Logger,   # A built-in middleware that automatically logs every request —
              # method, path, status code and response time. Super useful during development.

    Response, # Every handler must return a Response.
              # It wraps your data, the HTTP status code and any headers
              # into a valid HTTP response that gets sent back to the client.

    HttpCode  # An enum with all the standard HTTP status codes.
              # 200 OK, 201 Created, 404 Not Found, 500 Internal Server Error...
              # Using an enum means no more magic numbers scattered around your code.
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Create a Handler
# ─────────────────────────────────────────────────────────────────────────────
#
# A Handler is the function responsible for processing a request and returning a response.
# Every route needs one. The rules are simple:
#
#   1. Extend the Handler class
#   2. Implement the handle() method
#   3. Always return a Response
#
# That's literally it. Zoe takes care of the rest — parsing the request,
# extracting path params, validating the body, injecting dependencies...
# Your job is just to implement handle() and return something meaningful.
#

class HelloHandler(Handler):
    def handle(self) -> Response:
        return Response(
            http_status_code=HttpCode.OK,       # 200 — everything went well!
            body={"message": "Hello, World!"}   # Zoe automatically serializes this to JSON
        )
        # See? No boilerplate, no decorators, no magic strings.
        # Just a class, a method and a response.

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Wire everything together
# ─────────────────────────────────────────────────────────────────────────────
user = {
    "nome": "Lucas",
    "idade": 23
    }

if __name__ == "__main__":

    # First, create the App instance.
    # Nothing is registered yet — think of this as an empty container.
    app: App = App()

    # Then, create the Server and point it to your app.
    # The Server is what opens port 8080 and starts listening for HTTP connections.
    # The only required argument is the App instance.
    server: Server = Server(application=app)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3 — Create a Route
    # ─────────────────────────────────────────────────────────────────────────
    #
    # A route is the combination of three things:
    #
    #   endpoint — the URL path (what comes after the host)
    #   method   — the HTTP method (GET, POST, PUT, PATCH, DELETE)
    #   handler  — the Handler instance that will process the request
    #
    # Fun fact: two routes can share the same endpoint as long as the method is different.
    # GET /hello and POST /hello are completely separate routes — totally valid!
    #
    from zoe import HttpMethod

    hello_route: Route = Route(
        endpoint="/hello",
        method=HttpMethod.GET,
        handler=HelloHandler()  # pass an instance, not the class itself
    )

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4 — Register everything with the App
    # ─────────────────────────────────────────────────────────────────────────
    #
    # Creating a route or middleware is not enough — you need to register it.
    # Use app.use() for everything: routes, routers and middlewares.
    # Nothing gets picked up by the server until it's registered here.
    #
    app.use(hello_route)
    app.use(Logger("Hello-World"))  # optional but highly recommended during development

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5 — Start the server
    # ─────────────────────────────────────────────────────────────────────────
    #
    # This is the last step. server.run() blocks and starts listening for connections.
    # By default Zoe serves on http://127.0.0.1:8080
    #
    # Go ahead and try it:
    #   curl http://127.0.0.1:8080/hello
    #   → {"message": "Hello, World!"}
    #
    server.run()