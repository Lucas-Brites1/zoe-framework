# Zoe 🐾

> A lightweight Python web framework. Simple by design, loyal to your codebase, and powerful by nature.

```
pip install zoe-framework
```

[![Python](https://img.shields.io/badge/python-3.11+-gold)](https://python.org)
[![Version](https://img.shields.io/badge/version-v0.1.0--alpha-orange)](https://pypi.org/project/zoe-framework)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-red)]()

---

## Why Zoe?

- **Zero dependencies** — pure Python standard library, nothing else
- **Type-aware handlers** — declare your body type, Zoe validates and injects it automatically
- **Built-in validation** — schema validation with rich error messages out of the box
- **Chainable API** — fluent router and middleware chaining
- **Dependency Injection** — register services once, inject anywhere via type hints
- **Auth ready** — Bearer, Basic and ApiKey support built in

---

## Quick Start

```python
from zoe import App, Server, Router, Handler, Response, HttpCode
from zoe import Model, Field, NotNull, Email, Length, Logger

class CreateUserDto(Model):
    login: str = Field(NotNull(), Length(min=3, max=50))
    email: str = Field(NotNull(), Email())

class CreateUserHandler(Handler):
    def handle(self, body: CreateUserDto) -> Response:
        return Response(HttpCode.CREATED, body={"user": body})

if __name__ == "__main__":
    app = App()
    app.use(Logger("MyApp")) \
       .use(Router("/users").POST("", CreateUserHandler()))

    Server(app).run()
```

```
  Zoe Framework · http://127.0.0.1:8080
  ready to serve 🐾
```

---

## Installation

Requires **Python 3.11+**. No additional dependencies.

```bash
pip install zoe-framework
```

---

## Core Concepts

### Handlers

Extend `Handler` and implement `handle()`. Access the request via `self.request`.

```python
class GetUserHandler(Handler):
    def handle(self) -> Response:
        user_id = self.request.path_params.user_id
        token   = self.request.auth.bearer_token
        page    = self.request.query_params.page
        return Response(HttpCode.OK, body={"id": user_id})
```

### Routing

Group routes under a `Router` with a shared prefix. Chain HTTP methods fluently.

```python
user_router = Router("/users")
user_router \
    .POST("",            CreateUserHandler()) \
    .GET("",             ListUsersHandler())  \
    .GET("/{user_id}",   GetUserHandler())    \
    .PUT("/{user_id}",   UpdateUserHandler()) \
    .DELETE("/{user_id}", DeleteUserHandler())

app.use(user_router)
```

### Models & Validation

Extend `Model` and annotate fields with `Field` and validators. Zoe validates the request body and returns **all errors at once**.

```python
class CreateUserDto(Model):
    login:    str = Field(NotNull(), Length(min=3, max=50))
    email:    str = Field(NotNull(), Email())
    age:      int = Field(NotNull(), Range(min=18, max=120))
    username: str = Field(NotNull(), Pattern(r"^[a-zA-Z0-9_]+$"))
```

**Validation error response:**
```json
{
  "error": {
    "type": "SCHEMA_VALIDATION_ERROR",
    "model": "CreateUserDto",
    "count": 2,
    "errors": [
      { "field": "email",  "code": "INVALID_FORMAT", "message": "..." },
      { "field": "age",    "code": "OUT_OF_RANGE",   "message": "..." }
    ]
  }
}
```

**Available validators:**

| Validator | Description |
|---|---|
| `NotNull()` | Field is required, cannot be null |
| `Email()` | Must be a valid email address |
| `Length(min, max)` | String or list length |
| `Range(min, max)` | Numeric range |
| `Pattern(regex)` | Must match a regex pattern |

### Middlewares

Register middlewares with `app.use()`. They execute in registration order.

```python
app.use(CORS(allowed_origins=["https://mysite.com"])) \
   .use(Logger("MyApp", verbose=False))               \
   .use(Limiter(max_requests=100, window_seconds=60)) \
   .use(user_router)
```

**Built-in middlewares:**

| Middleware | Description |
|---|---|
| `Logger(name, verbose)` | Color-coded request logs with response time |
| `Limiter(max_requests, window_seconds)` | IP-based rate limiting |
| `CORS(allowed_origins, allowed_methods, allowed_headers)` | CORS with preflight support |

**Custom middleware:**

```python
def auth_guard(request, next):
    if not request.auth.bearer_token:
        return Response(HttpCode.UNAUTHORIZED)
    return next(request)

app.use(auth_guard)
```

### Dependency Injection

Register any class instance with `Container.provide(Box(...))`. Zoe resolves dependencies automatically via type hints in `handle()`.

```python
from zoe import Container, Box

# register once at startup
Container.provide_many(
    Box(Database(dsn="postgresql://...")),
    Box(EmailService()),
)

# inject via type hint — no __init__ needed
class CreateUserHandler(Handler):
    def handle(self, body: CreateUserDto, db: Database, email: EmailService) -> Response:
        user = db.create(body)
        email.send_welcome(user.email)
        return Response(HttpCode.CREATED, body={"user": user})
```

For functions or multiple instances of the same class, use an explicit key:

```python
Container.provide(Box(my_function, key="my_function"))

class MyHandler(Handler):
    def handle(self, my_function: callable) -> Response:
        my_function()
        ...
```

### Auth

Access authentication headers via `self.request.auth`:

```python
token       = self.request.auth.bearer_token     # Bearer <token>
credentials = self.request.auth.basic_credentials # (username, password)
api_key     = self.request.auth.api_key           # ApiKey <key>
scheme      = self.request.auth.scheme            # "Bearer", "Basic", "ApiKey"
```

---

## Full Example

```python
from zoe import App, Server, Router, Handler, Response, HttpCode
from zoe import Model, Field, NotNull, Email, Length, Range
from zoe import Logger, Limiter, CORS, Container, Box

class CreateUserDto(Model):
    login:    str = Field(NotNull(), Length(min=3, max=50))
    email:    str = Field(NotNull(), Email())
    age:      int = Field(NotNull(), Range(min=18, max=120))

_users = {}

class CreateUserHandler(Handler):
    def handle(self, body: CreateUserDto) -> Response:
        user_id = str(len(_users) + 1)
        _users[user_id] = body
        return Response(HttpCode.CREATED, body={"id": user_id, "user": body})

class GetUserHandler(Handler):
    def handle(self) -> Response:
        user_id = self.request.path_params.user_id
        user = _users.get(user_id)
        if not user:
            return Response(HttpCode.NOT_FOUND, body={"error": "User not found"})
        return Response(HttpCode.OK, body={"user": user})

class ListUsersHandler(Handler):
    def handle(self) -> Response:
        page  = int(self.request.query_params.page or 1)
        limit = int(self.request.query_params.limit or 10)
        users = list(_users.values())
        start = (page - 1) * limit
        return Response(HttpCode.OK, body={
            "users": users[start:start + limit],
            "total": len(users),
            "page":  page,
        })

if __name__ == "__main__":
    user_router = Router("/users")
    user_router \
        .POST("",           CreateUserHandler()) \
        .GET("",            ListUsersHandler())  \
        .GET("/{user_id}",  GetUserHandler())

    app = App()
    app.use(CORS(allowed_origins=["http://localhost:3000"])) \
       .use(Logger("MyApp"))                                 \
       .use(Limiter(max_requests=100, window_seconds=60))    \
       .use(user_router)

    Server(app).run()
```

---

## Project Structure

```
your-project/
├── main.py
├── routers/
│   ├── user_router.py
│   └── post_router.py
├── handlers/
│   ├── user_handlers.py
│   └── post_handlers.py
├── schemas/
│   ├── user_dto.py
│   └── post_dto.py
└── services/
    ├── database.py
    └── email_service.py
```

---

## Status & Roadmap

Zoe is currently in **alpha**. The API may change between versions.

| Version | Focus | Status |
|---|---|---|
| `v0.1.0` | Core framework, routing, validation, DI, CORS | current |
| `v0.2.0` | Tests, optional fields, `Optional[T]` support | soon |
| `v0.3.0` | Multiple response types (HTML, File, Redirect) | soon|
| `v0.4.0` | File upload, multipart/form-data | soon|
| `v0.5.0` | Async/await support | soon |
| `v1.0.0` | Stable API, full docs, production-ready | soon |

> Not recommended for production use in this stage.

---

## About

Zoe is named after my Golden Retriever. The goal is to eventually build a meaningful project named after each of my dogs as a way to honor them. 🐾

**Zoe** — 5 years old, Golden Retriever, loves toys and naps
**Mayla** — 4 years old, Golden Retriever, loves walks and naps
**Clara** — 2 years old, Dachshund, obsessed with fetch

---

## License

MIT © [Lucas Silva Brites](https://github.com/Lucas-Brites1)
