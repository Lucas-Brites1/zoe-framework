class Model:
  def __init__(self: "Model", **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)

  def __getattr__(self: "Model", name: str) -> any:
    raise AttributeError(f"'{type(self).__name__}' has no field '{name}'")

  def to_dict(self: "Model") -> dict:
    return self.__dict__

  @classmethod
  def is_model(cls, class_reference: type) -> bool:
    for base in class_reference.__mro__:
      if base.__name__ == "Model":
          return True
    return False

