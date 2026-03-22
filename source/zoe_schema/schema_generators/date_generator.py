from zoe_schema.field_schema_generator import FieldGenerator
from zoe_exceptions.exc_internal_exc import InternalServerException, ZoeNonHttpError
from typing import Any
import datetime
from enum import Enum, auto

class DateFormat(Enum):
  DATETIME       = auto()
  STRING         = auto()
  UNIX_TIMESTAMP = auto()

  def convert(self, value: datetime.datetime | datetime.date) -> datetime.datetime | datetime.date | str | int:
    match self:
      case DateFormat.DATETIME:       return value
      case DateFormat.STRING:         return value.isoformat()
      case DateFormat.UNIX_TIMESTAMP:
        if isinstance(value, datetime.datetime):
          return int(value.timestamp())
        else:
          raise InternalServerException.from_non_http_error(
          ZoeNonHttpError(
            why="'DateFormat.UNIX_TIMESTAMP' is not compatible with 'Date.Today'",
            explain="'Date.Today' returns a date-only value with no time component.\nUnix timestamps require a full datetime with time information, so the conversion is not possible.",
            fix="Use 'DateFormat.STRING' or omit 'as_' to use the default 'DateFormat.DATETIME'.\n'DateFormat.UNIX_TIMESTAMP' is not supported for date-only values."
          )
        )

class Date:
  class Now(FieldGenerator):
    def __init__(self, as_: DateFormat = DateFormat.DATETIME, timezone: datetime.tzinfo | None = None) -> None:
      self.fmt = as_
      self.tz = timezone

    def generate(self, *args, **kwargs) -> Any:
      return self.fmt.convert(datetime.datetime.now(self.tz))

  class Today(FieldGenerator):
    def __init__(self, as_: DateFormat = DateFormat.DATETIME) -> None:
      self.fmt = as_

    def generate(self, *args, **kwargs):
      return self.fmt.convert(datetime.date.today())

  class After(FieldGenerator):
    def __init__( self,
                  weeks: float = 0,
                  days: float = 0,
                  hours: float = 0,
                  minutes: float = 0,
                  seconds: float = 0,
                  microseconds: float = 0,
                  milliseconds: float = 0,
                  as_: DateFormat = DateFormat.DATETIME
                ) -> None:
      self.fmt = as_
      self.delta: datetime.timedelta = datetime.timedelta(
        weeks=weeks, days=days, hours=hours, minutes=minutes,
        seconds=seconds, microseconds=microseconds, milliseconds=milliseconds
        )

    def generate(self, *args, **kwargs) -> Any:
      return self.fmt.convert(datetime.datetime.now() + self.delta)
