from typing import Any
from abc import ABC, abstractmethod

class FieldGenerator(ABC):
  @abstractmethod
  def generate(self) -> Any: ...
