## v0.4.1

### Bug fixes

- **@Singleton()** now guaranteed to create exactly one instance under concurrent load.
  Previously, burst traffic could instantiate the same service multiple times.

- **@Scoped()** now works correctly in production. Previously, scoped dependencies were
  never actually isolated per-request because the scope was never opened or closed.

- **@Injectable** now inherits annotations from parent classes. Attributes declared in
  a base class are now injected into subclasses automatically.

- **Date.Now()** now captures the current time at request time, not at server startup.
  Previously, all records in a long-running server got the same timestamp.

### New features

- **App.listen(port=8080)** — start the server without instantiating Server explicitly.

- **Automatic request headers** — every response now includes X-Request-ID,
  X-Response-Time, X-Powered-By, and X-Served-By out of the box.

- **Date arithmetic** — Date.Now() + timedelta(days=30) now returns a generator
  that produces a future date at request time.

- **Container.reset()** — clear all registered services. Useful for test isolation.

- **Startup validation** — misconfigured singletons now fail at boot instead of
  crashing on the first request.

### Coming in v0.5.0
Circuit Breaker, Retry, Timeout middleware.

### Coming in v0.6.0
WebSocket support, streaming responses, SSE.
