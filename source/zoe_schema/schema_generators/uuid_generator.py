from zoe_schema.field_schema_generator import FieldGenerator
from typing import Any
import uuid

class UUID(FieldGenerator):
  def generate(self, *args, **kwargs) -> Any:
    return str(uuid.uuid4())
