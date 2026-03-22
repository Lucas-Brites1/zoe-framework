from zoe import Model, Assert, Email, Max, Min, NotNull, Required, OneOf, Password, Pattern, Range, Field
from zoe_schema.model_engine import ModelEngine
from zoe_exceptions.exc_internal_exc import InternalServerException
from zoe_exceptions.schemas_exceptions.exc_aggregate import ZoeSchemaAggregateException, ZoeSchemaException
import pytest

@pytest.mark.parametrize(
    "email_data", [
      {"message_from": "lucasbrites303@gmail.com", "content": "..."},
      {"message_from": "guibrites05@gmail.com"}
    ]
)
def test_field_attr_required_true(email_data):
  with pytest.raises(InternalServerException):
    class EmailModel(Model):
      message_from: str | None = Field(required=True)
      content:      str | None = Field(required=True)

    ModelEngine.validate_and_create(EmailModel, email_data)

@pytest.mark.parametrize(
    "email_data", [
      {"message_from": "lucasbrites303@gmail.com", "content": "..."}
    ]
)
def test_field_attr_required_true_pass(email_data):
    class EmailModel(Model):
      message_from: str  = Field(required=True)
      content:      str  = Field(required=True)

    ModelEngine.validate_and_create(EmailModel, email_data)

@pytest.mark.parametrize(
    "email_data", [
      {"message_from": "guibrites05@gmail.com"}
    ]
)
def test_field_attr_required_true_fails(email_data):
  with pytest.raises(InternalServerException):
    class EmailModel(Model):
      message_from: str  = Field(required=True)
      content:      str  = Field(required=True)

    ModelEngine.validate_and_create(EmailModel, email_data)

@pytest.mark.parametrize(
    "email_data", [
      {"message_from": "lucasbrites303@gmail.com", "content": "..."}
    ]
)
def test_field_validator_required_should_pass(email_data):
  class EmailModelRequired(Model):
    message_from: str  = Field(Required())
    content:      str  = Field(Required())

  ModelEngine.validate_and_create(EmailModelRequired, email_data)


@pytest.mark.parametrize(
    "email_data", [
      {"message_from": "lucasbrites303@gmail.com"}
    ]
)
def test_field_validator_required_should_fail(email_data):
  with pytest.raises(ZoeSchemaAggregateException):
      class EmailModelRequired(Model):
        message_from: str  = Field(Required())
        content:      str  = Field(Required())
      ModelEngine.validate_and_create(EmailModelRequired, email_data)
