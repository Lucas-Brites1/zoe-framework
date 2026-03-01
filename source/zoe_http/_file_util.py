from pathlib import Path

class FileUtil:
    @staticmethod
    def root_path() -> str:
      return str(Path(__file__).parent.parent.parent)

    @staticmethod
    def find(filename: str, directory: str | None = None) -> Path | None:
        if directory:
            full_path = (Path(directory) / filename).resolve()
            abs_directory = Path(directory).resolve()
            if not str(full_path).startswith(str(abs_directory)):
                return None
            return full_path if full_path.exists() else None
        else:
            current = Path.cwd()
            while True:
                candidate = (current / filename).resolve()
                if candidate.exists():
                    return candidate
                parent = current.parent
                if parent == current:
                    return None
                current = parent

    @staticmethod
    def read(path: Path) -> bytes | None:
        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None
