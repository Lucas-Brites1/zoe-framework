from zoe_schema.model_engine import ModelEngine
from zoe_schema.model_schema import Model, Strict
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException, ZoeSchemaException

import pytest

class User(Model):
  name: str
  age:  int

@pytest.mark.parametrize("data", [
  {"name": None, "age": 23},
  {"name": "Lucas", "age": None},
  {"name": "Lucas"},
  {"name": None},
  {"age": 23},
  {"age": None},
  {},
])
def test_model_null_fields_should_raise_exception(data):
  with pytest.raises(ZoeSchemaAggregateException) as exc_info:
    ModelEngine.validate_and_create(User, data)

@Strict
class UserStrict(Model):
  name: str
  age:  int

@pytest.mark.parametrize("strict_data", [
    {"name": "Lucas", "age": 23, "adicional": "deve lancar"},
])
def test_model_strict_mode_should_raise(strict_data):
    with pytest.raises(ZoeSchemaAggregateException):
        ModelEngine.validate_and_create(UserStrict, strict_data)

@pytest.mark.parametrize("strict_data", [
    {"name": "Lucas", "age": 23},
])
def test_model_strict_mode_should_pass(strict_data):
    result = ModelEngine.validate_and_create(UserStrict, strict_data)
    assert result.name == "Lucas"
    assert result.age == 23

class UserOptionalFields(Model):
   name: str | None = None
   age: int | None = None

@pytest.mark.parametrize("data, expected_name, expected_age", [
    ({"name": "Lucas"}, "Lucas", None),
    ({"age": 23}, None, 23),
])
def test_model_with_optional_fields(data, expected_name, expected_age):
    user = ModelEngine.validate_and_create(UserOptionalFields, data)
    assert user.name == expected_name
    assert user.age == expected_age

