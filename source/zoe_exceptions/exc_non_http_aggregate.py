from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError

class ZoeNonHttpAggregate(ZoeNonHttpError):
    def __init__(self, errors: list[ZoeNonHttpError]) -> None:
        self.errors = errors
        super().__init__(exception_message=self._format_errors())
    
    def _format_errors(self) -> str:
        count = len(self.errors)
        
        header = f"\n{count} Dependency Injection Error{'s' if count > 1 else ''}:\n"
        separator = "\n" + "="*70 + "\n"
        
        formatted = [header]
        
        for i, error in enumerate(self.errors, 1):
            formatted.append(f"\n{i}. {error.exception_message}\n")
        
        return separator.join([""] + formatted + [""])
    
    def __str__(self) -> str:
        return self.exception_message
    
    def __repr__(self) -> str:
        return f"ZoeNonHttpAggregate({len(self.errors)} errors)"