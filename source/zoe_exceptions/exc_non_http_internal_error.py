class ZoeNonHttpError(Exception):
    def __init__(self, exception_message: str) -> None:
        super().__init__(exception_message)
        self.exception_message = exception_message

    