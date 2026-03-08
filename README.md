# Zoe 🐾

> A lightweight Python web framework. Simple by design, loyal to your codebase, and powerful by nature.

```bash
pip install zoe-framework
```

[![Python](https://img.shields.io/badge/python-3.11+-gold)](https://python.org)
[![Version](https://img.shields.io/badge/version-v0.1.0--alpha-orange)](https://pypi.org/project/zoe-framework)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-red)]()

**Full documentation at [zoe-framework.dev](https://zoe-framework.dev)**

---

## Why Zoe?

- **Zero dependencies** — pure Python standard library, nothing else
- **Type-aware handlers** — declare your body type, Zoe validates and injects it automatically
- **Built-in validation** — schema validation with rich, aggregated error messages out of the box
- **Dependency Injection** — register services once, inject anywhere via type hints with `@Singleton`, `@Transient`, and `@Scoped`
- **Multipart support** — file uploads with typed field access out of the box
- **Auth ready** — Bearer, Basic and ApiKey support built in
- **Lifecycle hooks** — `@app.on_startup` and `@app.on_shutdown` for resource management

---

## Quick Start

```python
from zoe import App, Server, Router, Request, Response, HttpCode

router = Router(prefix="/")

@router.get("/hello")
def hello(req: Request) -> Response:
    return Response.text(HttpCode.OK, text="Hello, world!")

if __name__ == "__main__":
    app = App()
    app.use(router)
    Server(application=app).run()
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

### Routing

Define routes with function decorators or class-based handlers. Group routes under a `Router` with a shared prefix.

**Function-based:**
```python
router = Router(prefix="/users")

@router.get("/{user_id}")
def get_user(req: Request) -> Response:
    user_id = req.path_params.get("user_id")
    return Response.json(HttpCode.OK, body={"id": user_id})

@router.post("/")
def create_user(req: Request) -> Response:
    return Response.json(HttpCode.CREATED, body={"created": True})
```

**Class-based:**
```python
from zoe import Handler

class GetUserHandler(Handler):
    def handle(self, req: Request) -> Response:
        user_id = req.path_params.get("user_id")
        return Response.json(HttpCode.OK, body={"id": user_id})
```

---

### Request

Access everything about the incoming request through the `Request` object:

```python
@router.get("/example/{id}")
def example(req: Request) -> Response:
    # Path params
    user_id = req.path_params.get("id")

    # Query params — with type coercion and default
    page  = req.query_params.get("page",  type_=int, default=1)
    limit = req.query_params.get("limit", type_=int, default=10)

    # Auth
    token       = req.auth.bearer_token
    credentials = req.auth.basic_credentials  # (username, password)
    api_key     = req.auth.api_key

    # Headers
    content_type = req.content_type

    return Response.json(HttpCode.OK, body={})
```

---

### Response

Zoe provides typed response builders for every content type:

```python
# JSON — accepts dicts, lists, Model instances
Response.json(HttpCode.OK, body={"key": "value"})

# Plain text
Response.text(HttpCode.OK, text="Hello!")

# HTML
Response.html(HttpCode.OK, html_content="<h1>Hello</h1>")

# Redirect
Response.redirect(HttpCode.FOUND, redirect_to="/new-path")

# File — serves inline or as download
Response.file(HttpCode.OK, filename="report.pdf", directory="./files")
Response.file(HttpCode.OK, filename="data.csv", force_download=True)
```

---

### Models & Validation

Extend `Model` and annotate fields with `Field` and validators. Zoe validates the request body automatically and returns **all errors at once**.

```python
from zoe import Model, Field, NotNull, Email, Min, Max, Password, Pattern

class CreateUserDto(Model):
    name:     str = Field(NotNull())
    email:    str = Field(NotNull(), Email())
    age:      int = Field(NotNull(), Min(18), Max(120))
    password: str = Field(NotNull(), Password())
    username: str = Field(NotNull(), Pattern(r"^[a-zA-Z0-9_]+$"))

@router.post("/users")
def create_user(req: Request, body: CreateUserDto) -> Response:
    # body is already validated and instantiated
    return Response.json(HttpCode.CREATED, body=body.to_dict())
```

**Validation error response:**
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

**Available validators:**

| Validator | Description |
|---|---|
| `NotNull()` | Field is required, cannot be null |
| `Email()` | Must be a valid email address |
| `Password()` | Must meet password strength requirements |
| `Min(n)` | Minimum numeric value or string/list length |
| `Max(n)` | Maximum numeric value or string/list length |
| `Range(min, max)` | Numeric range |
| `Pattern(regex)` | Must match a regex pattern |
| `OneOf(*values)` | Must be one of the given values |
| `Assert(fn, msg)` | Custom assertion function |

---

### File Uploads

Access multipart form data via `req.multipart`:

```python
@router.post("/upload")
def upload(req: Request) -> Response:
    # Single file
    photo = req.multipart.file("photo")          # UploadFile | None
    saved = photo.save(path="./uploads", from_root=True, create_dirs=True)

    # Multiple files with same field name
    attachments = req.multipart.files("attachments")  # list[UploadFile] | None

    # Text fields
    title = req.multipart.field("title")              # str | None
    count = req.multipart.field("count", type_=int)   # int | None

    return Response.json(HttpCode.OK, body={"saved": str(saved)})
```

**UploadFile properties:**
```python
photo.filename   # original filename
photo.file_type  # MIME type (e.g. "image/jpeg")
photo.size       # size in bytes
photo.data_bytes # raw bytes
photo.text       # decoded as UTF-8 (for text files only)
```

---

### Dependency Injection

Register services with `@Singleton`, `@Transient`, or `@Scoped`. Zoe resolves and injects them via type hints — no boilerplate.

```python
from zoe import Singleton, Transient, Scoped

@Singleton(host="localhost", port=5432)
class Database:
    def __init__(self, host: str, port: int):
        self.conn = connect(host, port)

    def query(self, sql: str): ...

@router.get("/users")
def list_users(req: Request, db: Database) -> Response:
    users = db.query("SELECT * FROM users")
    return Response.json(HttpCode.OK, body=users)
```

**Lifecycle comparison:**

| Decorator | Behavior |
|---|---|
| `@Singleton()` | One instance shared across the entire application |
| `@Transient()` | New instance created every time it's resolved |
| `@Scoped()` | One instance per request, shared within that request |

---

### Middlewares

Register middlewares with `app.use()`. They execute in registration order.

```python
from zoe import Logger, Limiter, CORS, Helmet, BodyLimiter, Guard, BearerStrategy

app = App()
app.use(CORS(allowed_origins=["https://mysite.com"]))
app.use(Logger())
app.use(Limiter(max_requests=100, window_seconds=60))
app.use(Helmet())
app.use(BodyLimiter(max_size_mb=5))
app.use(Guard(strategy=BearerStrategy(secret="my-secret")))
app.use(router)
```

**Built-in middlewares:**

| Middleware | Description |
|---|---|
| `Logger()` | Color-coded request logs with response time |
| `Limiter(max_requests, window_seconds)` | IP-based rate limiting |
| `CORS(...)` | CORS with preflight support |
| `Helmet()` | Security headers (XSS, HSTS, etc.) |
| `BodyLimiter(max_size_mb)` | Limit request body size |
| `Guard(strategy)` | Auth enforcement — Bearer, Basic, ApiKey |
| `StaticFiles(directory)` | Serve static files |

**Custom middleware:**

```python
from zoe import Middleware, Request, Response

class MyMiddleware(Middleware):
    def process(self, request: Request, next) -> Response:
        print(f"Before: {request.route}")
        response = next(request)
        print(f"After: {response.status_code}")
        return response
```

---

### Lifecycle Hooks

Run code before the server starts accepting requests or after it shuts down:

```python
app = App()

@app.on_startup()
def connect():
    print("Connecting to database...")

@app.on_shutdown()
def disconnect():
    print("Closing connections...")

Server(application=app).run()
```

---

### Environment Variables

```python
from zoe import Env

db_url  = Env.get("DATABASE_URL")
port    = Env.get("PORT", default="8080")
debug   = Env.get_bool("DEBUG", default=False)
```

---

## Full Example

```python
from zoe import App, Server, Router, Request, Response, HttpCode
from zoe import Model, Field, NotNull, Email, Min, Max
from zoe import Singleton, Logger, CORS, Limiter

@Singleton()
class UserRepository:
    def __init__(self):
        self._users = {}

    def create(self, name: str, email: str) -> dict:
        user_id = str(len(self._users) + 1)
        self._users[user_id] = {"id": user_id, "name": name, "email": email}
        return self._users[user_id]

    def find_all(self) -> list:
        return list(self._users.values())

    def find(self, user_id: str) -> dict | None:
        return self._users.get(user_id)

class CreateUserDto(Model):
    name:  str = Field(NotNull())
    email: str = Field(NotNull(), Email())
    age:   int = Field(NotNull(), Min(18), Max(120))

router = Router(prefix="/users")

@router.post("/")
def create_user(req: Request, body: CreateUserDto, repo: UserRepository) -> Response:
    user = repo.create(name=body.name, email=body.email)
    return Response.json(HttpCode.CREATED, body=user)

@router.get("/")
def list_users(req: Request, repo: UserRepository) -> Response:
    return Response.json(HttpCode.OK, body=repo.find_all())

@router.get("/{user_id}")
def get_user(req: Request, repo: UserRepository) -> Response:
    user_id = req.path_params.get("user_id")
    user = repo.find(user_id)
    if user is None:
        return Response.json(HttpCode.NOT_FOUND, body={"error": "User not found"})
    return Response.json(HttpCode.OK, body=user)

if __name__ == "__main__":
    app = App()
    app.use(CORS(allowed_origins=["http://localhost:3000"]))
    app.use(Logger())
    app.use(Limiter(max_requests=100, window_seconds=60))
    app.use(router)

    @app.on_startup()
    def on_start():
        print("Server is ready!")

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
└── services/
    ├── user_repository.py
    └── email_service.py
```

---

## Status & Roadmap

Zoe is currently in **alpha**. The API may change between versions.

| Version | Focus | Status |
|---|---|---|
| `v0.1.0` | Core framework, routing, validation, DI, middlewares, multipart | **current** |
| `v0.2.0` | Test client, optional fields, `Optional[T]` support | soon |
| `v0.3.0` | OpenAPI/Swagger generation from Models | soon |
| `v0.4.0` | Async/await support | planned |
| `v1.0.0` | Stable API, full docs, production-ready | planned |

> Not recommended for production use at this stage.

---

## About

Zoe is named after my Golden Retriever. The goal is to eventually build a meaningful project named after each of my dogs. 🐾

- **Zoe** — 5 years old, Golden Retriever, loves toys and naps
- **Mayla** — 4 years old, Golden Retriever, loves walks and naps
- **Clara** — 2 years old, Dachshund, obsessed with fetch

---

## License

MIT © [Lucas Silva Brites](https://github.com/Lucas-Brites1)
