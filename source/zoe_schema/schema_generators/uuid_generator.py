from zoe_schema.field_schema_generator import FieldGenerator
from typing import Any
import uuid

class UUID(FieldGenerator):
  def generate(self, *args, **kwargs) -> Any:
    return str(uuid.uuid4())

  @staticmethod
  def is_valid(value: str) -> bool:
    import re
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, value, re.IGNORECASE))

