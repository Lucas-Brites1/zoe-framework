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
  def data(self: "UploadFile") -> str:
    return self.__data_bytes.decode(encoding="utf-8")

  @property
  def filename(self: "UploadFile") -> str:
    return self.__filename

  @property
  def file_type(self: "UploadFile") -> str:
    return self.__type
