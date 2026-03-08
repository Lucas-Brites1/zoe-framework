from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError

class ZoeNonHttpAggregate(ZoeNonHttpError):
    def __init__(self, errors: list[ZoeNonHttpError]) -> None:
        self.errors = errors
        count = len(errors)
        super().__init__(
            why=f"{count} Dependency Injection Error{'s' if count > 1 else ''}",
            explain="\n\n".join(e.explain for e in errors),
            fix="\n\n".join(e.fix for e in errors)
        )

    def __repr__(self) -> str:
        return f"ZoeNonHttpAggregate({len(self.errors)} errors)"
