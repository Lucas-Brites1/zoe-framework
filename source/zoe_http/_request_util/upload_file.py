from zoe_http._file_util import FileUtil
from zoe_http._file_util import ROOT, Path
import uuid
class UploadFile:
  def __init__(self: "UploadFile", filename: str, type: str, data_bytes: bytes) -> None:
    self.__filename = filename
    self.__type = type
    self.__data_bytes = data_bytes

  @property
  def size(self: "UploadFile") -> int:
    return len(self.__data_bytes)

  @property
  def data_bytes(self: "UploadFile") -> bytes:
    return self.__data_bytes

  @property
  def text(self: "UploadFile") -> str:
    return self.__data_bytes.decode(encoding="utf-8")

  @property
  def filename(self: "UploadFile") -> str:
    return self.__filename

  @property
  def file_type(self: "UploadFile") -> str:
    return self.__type

  def save(self, path: str, froom_root: bool, filename: str | None = None, create_dirs: bool = False) -> Path | None:
    filename_to_save = filename or self.filename
    directory_path: Path = Path(path)
    if froom_root:
      directory_path = ROOT / directory_path

    if not directory_path.exists():
      if create_dirs:
        FileUtil.create_directory(directory_path)
      else:
        return None

    full_path: Path
    if (directory_path / filename_to_save).exists():
      p = Path(filename_to_save)
      filename_to_save = f"{p.stem}_{uuid.uuid4()}{p.suffix}"

    full_path = directory_path / filename_to_save

    commited: bool = FileUtil.write(path=full_path, bytes_=self.data_bytes)

    return full_path if commited else None
