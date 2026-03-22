# 🐾 Zoe

A lightweight Python web framework. Zero dependencies, type-aware injection, aggregated validation.

```bash
pip install zoe-framework
```

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![Version](https://img.shields.io/badge/version-v0.3.0-blue)](https://pypi.org/project/zoe-framework)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Full documentation at [zoe-framework.dev](https://zoe-framework.dev)

---

## Why Zoe?

- **Zero dependencies** — pure Python standard library
- **Fully async** — built on `asyncio.start_server`, supports async handlers and middlewares
- **Type-aware injection** — body, services, and request resolved automatically via type hints
- **Aggregated validation** — all field errors returned at once, never just the first
- **Three DI lifecycles** — `@Singleton`, `@Transient`, and `@Scoped` out of the box
- **Field generators** — auto-generate UUIDs, timestamps, tokens, slugs and more
- **Computed fields** — derive field values from other fields at request time
- **Multipart support** — file uploads with typed field access, no setup required
- **Rich middleware stack** — Logger, CORS, Limiter, Guard, Helmet, StaticFiles, BodyLimiter

---

## Quick Start

```python
from zoe import App, Server, Router, Request, Response, HttpCode

router = Router(prefix="/")

@router.get("/hello")
async def hello(req: Request) -> Response:
    return Response.text(HttpCode.OK, text="Hello, world!")

if __name__ == "__main__":
    app = App()
    app.use(router)
    Server(application=app).run()
```

---

## Routing

Routes can be registered using decorators or the explicit `router.add` / `Route` API.

### Decorator style (function-based)

```python
from zoe import Router, Request, Response, HttpCode

router = Router(prefix="/users")

@router.get("/")
async def list_users(req: Request) -> Response:
    return Response.json(HttpCode.OK, body=[])

@router.post("/")
async def create_user(req: Request) -> Response: ...

@router.get("/{user_id}")
async def get_user(req: Request) -> Response:
    user_id = req.path_params.get("user_id")
    return Response.json(HttpCode.OK, body={"id": user_id})

@router.put("/{user_id}")
async def update_user(req: Request) -> Response: ...

@router.patch("/{user_id}")
async def patch_user(req: Request) -> Response: ...

@router.delete("/{user_id}")
async def delete_user(req: Request) -> Response: ...
```

### Decorator style (class-based)

```python
from zoe import Handler, Request, Response, HttpCode

router = Router(prefix="/users")

@router.get("/{user_id}")
class GetUserHandler(Handler):
    async def handle(self, request: Request) -> Response:
        user_id = request.path_params.get("user_id")
        return Response.json(HttpCode.OK, body={"id": user_id})
```

### Explicit registration

```python
from zoe import Router, Route

router = Router(prefix="/users")
router.add(Route.get(endpoint="/{user_id}", handler=GetUserHandler()))
router.add(Route.post(endpoint="/", handler=CreateUserHandler()))
router.add(Route.delete(endpoint="/{user_id}", handler=DeleteUserHandler()))
```

---

## Handlers

Every handler receives a `Request` and must return a `Response`. Handlers can be sync or async.

### Function-based

```python
@router.get("/{user_id}")
async def get_user(req: Request) -> Response:
    user_id = req.path_params.get("user_id")
    return Response.json(HttpCode.OK, body={"id": user_id})
```

The `Request` parameter can be named anything as long as it is typed as `Request`.

### Class-based

```python
class GetUserHandler(Handler):
    async def handle(self, request: Request) -> Response:
        user_id = request.path_params.get("user_id")
        return Response.json(HttpCode.OK, body={"id": user_id})
```

The `Request` parameter in class-based handlers must be named `request` — Zoe uses this name to distinguish it from injected services.

---

## Request

```python
@router.get("/example/{id}")
async def example(req: Request) -> Response:
    # Path params
    user_id = req.path_params.get("id")

    # Query params — with optional type coercion and default
    page  = req.query_params.get("page",  type_=int, default=1)
    limit = req.query_params.get("limit", type_=int, default=10)

    # Headers
    content_type = req.headers.get("content-type")

    # Auth
    token       = req.auth.bearer_token
    credentials = req.auth.basic_credentials  # (username, password)
    api_key     = req.auth.api_key

    return Response.json(HttpCode.OK, body={})
```

---

## Response

```python
# JSON — accepts dicts, lists, Model instances
Response.json(HttpCode.OK, body={"key": "value"})

# Plain text
Response.text(HttpCode.OK, text="Hello")

# HTML
Response.html(HttpCode.OK, html_content="<h1>Hello</h1>")

# Redirect
Response.redirect(HttpCode.FOUND, redirect_to="/new-path")

# File — inline or forced download
Response.file(HttpCode.OK, filename="report.pdf", directory="./files")
Response.file(HttpCode.OK, filename="data.csv", force_download=True)
```

---

## Models and Validation

Extend `Model` and annotate fields with `Field` and validators. Zoe validates the request body automatically and returns all errors at once.

### Basic usage

```python
from zoe import Model, Field, NotNull, Email, Min, Max, Password, Pattern, OneOf, Assert

class CreateUserDto(Model):
    name:     str = Field(NotNull())
    email:    str = Field(NotNull(), Email())
    age:      int = Field(NotNull(), Min(18), Max(120))
    password: str = Field(NotNull(), Password())
    role:     str = Field(NotNull(), OneOf("admin", "user", "guest"))

@router.post("/users")
async def create_user(req: Request, body: CreateUserDto) -> Response:
    return Response.json(HttpCode.CREATED, body=body.to_dict())
```

### Optional fields and defaults

```python
class UpdateUserDto(Model):
    name:  str | None = Field()                 # optional, no default
    email: str | None = Field()                 # optional, no default
    role:  str        = Field(default="user")   # required type, default value
```

### Field generators

Generators automatically produce values for fields that are absent from the request body.

```python
from zoe import UUID, Date, Token, Slug, DateFormat

class CreateUserDto(Model):
    id:         str      = Field(generator=UUID())
    created_at: datetime = Field(generator=Date.Now())
    token:      str      = Field(generator=Token(token_size=32))
    slug:       str      = Field(generator=Slug("user", random_part_size=8))

# Date generators
Date.Now()                                    # datetime with local timezone
Date.Now(timezone=timezone.utc)               # datetime with UTC timezone
Date.Now(as_=DateFormat.STRING)               # ISO 8601 string
Date.Now(as_=DateFormat.UNIX_TIMESTAMP)       # Unix timestamp (int)
Date.Today()                                  # date only (no time)
Date.After(days=30)                           # datetime 30 days from now
Date.After(weeks=2, hours=6)                  # datetime 2 weeks and 6 hours from now
```

### Computed fields

Derive a field value from other fields at request time.

```python
from zoe import ComputedField

class CreateProductDto(Model):
    name:  str = Field(NotNull())
    price: int = Field(NotNull())
    slug:  str = ComputedField(lambda fields: fields["name"].lower().replace(" ", "-"))
```

### Custom validators and generators

```python
from zoe import FieldValidator, FieldGenerator, Field
from zoe_exceptions.schemas_exceptions.exc_validator import SchemaValidatorException

class EvenNumber(FieldValidator):
    def validate(self, value, field_name):
        if value % 2 != 0:
            raise SchemaValidatorException(field_name=field_name, message=f"{field_name} must be even.")

class PrefixedID(FieldGenerator):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def generate(self):
        import uuid
        return f"{self.prefix}-{uuid.uuid4()}"

class MyDto(Model):
    count: int = Field(EvenNumber())
    id:    str = Field(generator=PrefixedID("usr"))
```

### Required validator

`Required()` differs from `NotNull()` in intent: it asserts that the field must be explicitly present in the body, regardless of type.

```python
class CreatePostDto(Model):
    title:   str = Field(Required())
    content: str = Field(Required())
```

### Nested models

```python
class AddressDto(Model):
    street: str = Field(NotNull())
    city:   str = Field(NotNull())
    zip:    str = Field(NotNull(), Pattern(r"^\d{5}$"))

class CreateUserDto(Model):
    name:    str        = Field(NotNull())
    email:   str        = Field(NotNull(), Email())
    address: AddressDto = Field(NotNull())
```

Nested models are validated recursively. Errors from nested fields are included in the same aggregated response.

### Strict mode

```python
from zoe import Strict

@Strict
class StrictDto(Model):
    name: str = Field(NotNull())
    # extra fields in the body will return a 400 error
```

### Validation error response

```json
{
  "error": {
    "type": "SCHEMA_VALIDATION_ERROR",
    "model": "CreateUserDto",
    "count": 2,
    "errors": [
      { "field": "email",    "code": "INVALID_FORMAT", "message": "..." },
      { "field": "password", "code": "WEAK_PASSWORD",  "message": "..." }
    ]
  }
}
```

### Available validators

| Validator | Description |
|---|---|
| `NotNull()` | Value must not be null |
| `Required()` | Field must be present in the body |
| `Email()` | Must be a valid email address |
| `Password()` | Must meet password strength requirements |
| `Min(n)` | Minimum numeric value or string/list length |
| `Max(n)` | Maximum numeric value or string/list length |
| `Range(min, max)` | Numeric range |
| `Pattern(regex)` | Must match a regex pattern |
| `OneOf(*values)` | Must be one of the given values |
| `Assert(fn, msg)` | Custom assertion function |

---

## Dependency Injection

Register services with `@Singleton`, `@Transient`, or `@Scoped`. Zoe resolves them by type in handler parameters.

```python
from zoe import Singleton, Transient, Scoped

@Singleton()
class Database:
    def __init__(self):
        self.conn = connect(...)

@Transient()
class EmailService:
    def send(self, to: str, subject: str): ...

@router.post("/users")
async def create_user(req: Request, body: CreateUserDto, db: Database, email: EmailService) -> Response:
    user = db.create(body.name, body.email)
    email.send(user.email, "Welcome")
    return Response.json(HttpCode.CREATED, body={"id": user.id})
```

You can pass constructor arguments directly in the decorator:

```python
@Singleton(host="localhost", port=5432)
class Database:
    def __init__(self, host: str, port: int):
        self.conn = connect(host, port)
```

### Lifecycle comparison

| Decorator | Behavior |
|---|---|
| `@Singleton()` | One instance shared across the entire application |
| `@Transient()` | New instance created on every injection |
| `@Scoped()` | One instance per request, shared within that request |

---

## File Uploads

```python
@router.post("/upload")
async def upload(req: Request) -> Response:
    photo       = req.multipart.file("photo")           # UploadFile | None
    attachments = req.multipart.files("attachments")    # list[UploadFile] | None
    title       = req.multipart.field("title")          # str | None
    count       = req.multipart.field("count", type_=int)

    saved = photo.save(path="./uploads", create_dirs=True)
    return Response.json(HttpCode.OK, body={"saved": str(saved)})
```

**UploadFile properties:**

| Property | Description |
|---|---|
| `filename` | Original filename from the form |
| `file_type` | MIME type (e.g. `image/jpeg`) |
| `size` | File size in bytes |
| `data_bytes` | Raw bytes |
| `text` | Decoded content as UTF-8 (text files only) |

---

## Middlewares

```python
from zoe import Logger, Limiter, CORS, Helmet, BodyLimiter, Guard, BearerStrategy, StaticFiles

app = App()
app.use(CORS(allowed_origins=["https://mysite.com"]))
app.use(Logger())
app.use(Limiter(max_requests=100, window_seconds=60))
app.use(Helmet())
app.use(BodyLimiter(max_size_mb=5))
app.use(StaticFiles(directory="./public", prefix="/static"))
app.use(Guard(strategy=BearerStrategy(secret="my-secret")))
app.use(router)
```

### Built-in middlewares

| Middleware | Description |
|---|---|
| `Logger()` | Color-coded request logs with timing |
| `Limiter(max_requests, window_seconds)` | IP-based rate limiting |
| `CORS(allowed_origins, ...)` | CORS headers with preflight support |
| `Helmet()` | Security headers (XSS, HSTS, etc.) |
| `BodyLimiter(max_size_mb)` | Reject oversized request bodies |
| `Guard(strategy)` | Auth enforcement — Bearer, Basic, ApiKey |
| `StaticFiles(directory, prefix)` | Serve static files |

### Guard strategies

```python
from zoe import Guard, BearerStrategy, BasicStrategy, ApiKeyStrategy, AnyStrategy, AllStrategy

Guard(BearerStrategy(secret="token"))
Guard(ApiKeyStrategy(key="key123"))
Guard(AnyStrategy([BearerStrategy(secret="token"), ApiKeyStrategy(key="key123")]))
Guard(AllStrategy([BearerStrategy(secret="token"), ApiKeyStrategy(key="key123")]))
```

Attach `Guard` to a specific `Router` to protect only those routes:

```python
admin_router = Router(prefix="/admin")
admin_router.use(Guard(BearerStrategy(secret="secret")))
```

### Custom middleware

```python
from zoe import AsyncMiddleware, Request, Response

class TimingMiddleware(AsyncMiddleware):
    async def process(self, request: Request, next) -> Response:
        import time
        start = time.time()
        response = await next(request)
        response.headers.add("X-Response-Time", f"{time.time() - start:.3f}s")
        return response
```

---

## Lifecycle Hooks

```python
app = App()

@app.on_startup()
def on_start():
    print("Connecting to database...")

@app.on_shutdown()
def on_stop():
    print("Closing connections...")

Server(application=app).run()
```

---

## Environment

```python
from zoe import Env

db_url = Env.get("DATABASE_URL")
port   = Env.get("PORT", default="8080")
debug  = Env.get_bool("DEBUG", default=False)
```

---

## Exceptions

```python
from zoe import ZoeHttpException, NotFoundException, HttpCode

raise ZoeHttpException(message="Forbidden", status_code=HttpCode.FORBIDDEN)
raise NotFoundException(resource="User", identifier=user_id)
```

---

## Full Example

```python
from zoe import App, Server, Router, Request, Response, HttpCode
from zoe import Model, Field, NotNull, Email, Min, Max
from zoe import UUID, Date
from zoe import Singleton, Logger, CORS, Limiter
from datetime import datetime

@Singleton()
class UserRepository:
    def __init__(self):
        self._users: dict = {}

    def create(self, id: str, name: str, email: str) -> dict:
        self._users[id] = {"id": id, "name": name, "email": email}
        return self._users[id]

    def find_all(self) -> list:
        return list(self._users.values())

    def find(self, uid: str) -> dict | None:
        return self._users.get(uid)


class CreateUserDto(Model):
    id:         str      = Field(generator=UUID())
    created_at: datetime = Field(generator=Date.Now())
    name:       str      = Field(NotNull())
    email:      str      = Field(NotNull(), Email())
    age:        int      = Field(NotNull(), Min(18), Max(120))


router = Router(prefix="/users")

@router.post("/")
async def create_user(req: Request, body: CreateUserDto, repo: UserRepository) -> Response:
    user = repo.create(body.id, body.name, body.email)
    return Response.json(HttpCode.CREATED, body=user)

@router.get("/")
async def list_users(req: Request, repo: UserRepository) -> Response:
    return Response.json(HttpCode.OK, body=repo.find_all())

@router.get("/{user_id}")
async def get_user(req: Request, repo: UserRepository) -> Response:
    user = repo.find(req.path_params.get("user_id"))
    if user is None:
        return Response.json(HttpCode.NOT_FOUND, body={"error": "User not found"})
    return Response.json(HttpCode.OK, body=user)


if __name__ == "__main__":
    app = App()
    app.use(CORS()).use(Logger()).use(Limiter(max_requests=100, window_seconds=60)).use(router)

    @app.on_startup()
    def on_start():
        print("Server ready.")

    Server(application=app).run()
```

---

## Project Structure

```
your-project/
├── main.py
├── routers/
│   ├── user_router.py
│   └── post_router.py
├── dtos/
│   ├── user_dto.py
│   └── post_dto.py
├── services/
│   ├── user_repository.py
│   └── email_service.py
└── database/
    └── connection.py
```

---

## Roadmap

| Version | Focus | Status |
|---|---|---|
| `v0.1.0-alpha` | Core routing, validation, basic DI, middlewares | released |
| `v0.2.0` | 3 DI lifecycles, multipart, all response types, Guard, Helmet, StaticFiles, nested models, Env | released |
| `v0.3.0` | Full async support, field generators, ComputedField, early config validation, unit tests | current |
| `v0.4.0` | Global exception handler, test client, Container.reset() | planned |
| `v0.5.0` | Auto-documentation (`/docs` route, OpenAPI/JSON output) | planned |
| `v1.0.0` | Stable API, full documentation, production-ready | planned |

---

## License

MIT — Lucas Silva Brites
