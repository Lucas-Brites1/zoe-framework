from pathlib import Path

class FileUtil:
    @staticmethod
    def root_path() -> str:
      return str(Path(__file__).parent.parent.parent)

    @staticmethod
    def create_directory(directory: Path) -> None:
      directory.mkdir(parents=True, exist_ok=True)

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
    def resolve_path(directory: str, filename: str) -> Path:
        return Path(directory) / filename


    @staticmethod
    def write(path: Path, bytes_: bytes) -> bool:
        try:
            with open(path, "wb") as f:
                f.write(bytes_)
            return True
        except Exception as e:
            return False

    @staticmethod
    def read(path: Path) -> bytes | None:
        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

ROOT = FileUtil.root_path()
