from enum import Enum

from zoe_middlewares.logger import _Color

reset_color: str = _Color.RESET


class LogLevel(Enum):
    INFO = ("INFO", _Color.GREEN)
    DEBUG = ("DEBUG", _Color.CYAN)
    WARNING = ("WARNING", _Color.YELLOW)
    ERROR = ("ERROR", _Color.RED)
    CRITICAL = ("CRITICAL", _Color.MAGENTA)
    STACKTRACE = ("STACKTRACE", _Color.GREY)

    @property
    def label(self) -> str:
        return self.value[0]

    @property
    def color(self) -> str:
        return self.value[1]
