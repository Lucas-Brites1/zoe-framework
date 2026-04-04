from pathlib import Path
import sys

class FileUtil:
    BASE_DIR: Path = Path(sys.argv[0]).resolve().parent if (sys.argv and sys.argv[0]) else Path.cwd()
    WORKING_DIR: Path = Path.cwd()
    FRAMEWORK_DIR: Path = Path(__file__).resolve().parent.parent

    @staticmethod
    def mount_path(*segments: str, start_from: Path = BASE_DIR) -> Path:
        path = start_from
        for segment in segments:
            path = path / segment.strip("/\\")
        return path

    @staticmethod
    def find_upwards(filename: str, start_dir: Path = WORKING_DIR) -> Path | None:
        current = start_dir.resolve()
        while True:
            candidate = current / filename
            if candidate.exists():
                return candidate

            parent = current.parent
            if parent == current:
                return None
            current = parent

    @staticmethod
    def read_internal(relative_path_from_zoe: str) -> bytes | None:
        full_path = FileUtil.mount_path(relative_path_from_zoe, start_from=FileUtil.FRAMEWORK_DIR)
        return FileUtil.read(full_path)

    @staticmethod
    def create_directory(directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def write(path: Path, bytes_: bytes) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bytes_)
            return True
        except Exception:
            return False

    @staticmethod
    def read(path: Path) -> bytes | None:
        try:
            return path.read_bytes()
        except (FileNotFoundError, PermissionError):
            return None
