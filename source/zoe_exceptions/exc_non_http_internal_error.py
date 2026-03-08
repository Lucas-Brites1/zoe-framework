class ZoeNonHttpError(Exception):
    def __init__(
        self,
        why: str,          # "Unresolved dependency 'db: Database'"
        explain: str,      # "The parameter 'db' of type 'Database' was not found..."
        fix: str,          # "@Singleton\nclass Database: ..."
    ) -> None:
        self.why = why
        self.explain = explain
        self.fix = fix
        super().__init__(why)
