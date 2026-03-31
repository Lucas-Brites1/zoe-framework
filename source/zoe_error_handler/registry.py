from zoe_error_handler.error_handler_protocol import ErrorHandler
from zoe_exceptions.http_exceptions.exc_domain import DomainException
from zoe_exceptions.exc_internal_exc import InternalServerException, ZoeNonHttpError
from threading import RLock

class DomainErrorDispatcher:
  _handlers: list[tuple[type[DomainException], ErrorHandler]] = []
  _rlock: RLock = RLock()

  @classmethod
  def register(cls, matcher: type[DomainException], handler: ErrorHandler) -> None:
    if isinstance(matcher, type):
        if not issubclass(matcher, DomainException):
            raise InternalServerException.from_non_http_error(
                error=ZoeNonHttpError(
                    why=f"@on_error does not accept '{matcher.__name__}' as a matcher",
                    explain=(
                        f"'{matcher.__name__}' does not inherit from DomainException.\n"
                        f"@on_error only handles domain exceptions that the application "
                        f"explicitly defines and raises."
                    ),
                    fix="class MyError(DomainException): ..."
                )
            )
    else:
        raise InternalServerException.from_non_http_error(
            error=ZoeNonHttpError(
                why=f"@on_error received an invalid matcher of type '{type(matcher).__name__}'",
                explain=(
                    f"Expected a DomainException subclass, "
                    f"but received an instance of '{type(matcher).__name__}' instead.\n"
                    f"Make sure you are passing the class itself, not an instance of it."
                ),
                fix=(
                    f"@on_error(MyError)          ← correct: the class\n"
                    f"@on_error(MyError())         ← wrong: an instance"
                )
            )
        )

    with cls._rlock:
        cls._handlers.append((matcher, handler))

  @classmethod
  def resolve(cls, exc: Exception) -> ErrorHandler | None:
    with cls._rlock:
       handlers: list[tuple[type[DomainException], ErrorHandler]] = cls._handlers.copy()

    candidates = [
        (matcher, handler)
        for matcher, handler in handlers
        if cls._matches(matcher, exc)
    ]

    if not candidates:
        return None

    candidates.sort(
        key=lambda pair: len(pair[0].__mro__),
        reverse=True
    )

    return candidates[0][1]

  @classmethod
  def _matches(cls, matcher: type[DomainException], exception: Exception) -> bool:
    return isinstance(exception, matcher)

  @classmethod
  def reset(cls) -> None:
     with cls._rlock:
        cls._handlers.clear()

