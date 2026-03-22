from zoe_schema.field_schema_generator import FieldGenerator
from os import urandom
from base64 import urlsafe_b64encode
from math import ceil

class Token(FieldGenerator):
  def __init__(self, token_size: int) -> None:
    self.size = token_size

  def _required_bytes(self) -> int:
    # 3 bytes = 4 characters ~ 1 byte = 4/3 characters
    return ceil((self.size * 3) / 4)

  def generate(self) -> str:
    random_bytes: bytes = urandom(self._required_bytes())
    encoded_bytes: bytes = urlsafe_b64encode(random_bytes)
    return encoded_bytes.decode()[:self.size]
