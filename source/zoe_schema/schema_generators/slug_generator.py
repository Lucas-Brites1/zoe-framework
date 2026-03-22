from zoe_schema.field_schema_generator import FieldGenerator
import secrets

class Slug(FieldGenerator):
  _alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
  def __init__(self, *parts: str, random_part_size: int = 12) -> None:
    self.rdptsize = random_part_size
    self.parts = parts

  def generate(self):
    slug: str = ""
    for p in self.parts:
      slug += f"{p}-"

    rdpart: str = ""
    while len(rdpart) != self.rdptsize:
      rdpart += secrets.choice(self._alphabet)

    return slug + rdpart

