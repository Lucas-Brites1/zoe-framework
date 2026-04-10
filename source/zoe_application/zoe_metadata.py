from importlib.metadata import version, PackageNotFoundError
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zoe_application.application import App

from zoe_di.container import Container
from zoe_di.singleton import Singleton

class RuntimeEnvironment(Enum):
    HOMOLOGATION = "hom"
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"

dev = RuntimeEnvironment.DEVELOPMENT
prod = RuntimeEnvironment.PRODUCTION
hom = RuntimeEnvironment.HOMOLOGATION

class ZoeMeta(type):
    @property
    def instance(cls) -> "Zoe":
        return Container.resolve(ref=Zoe)

class Config:
    def __init__(self) -> None:
        self.__environment = dev
        self.__appname = "application"
        self.__appversion = "0.0.1"
        self.__debug = True

    @property
    def environment(self) -> RuntimeEnvironment:
        return self.__environment

    @property
    def appname(self) -> str:
        return self.__appname

    @property
    def appversion(self) -> str:
        return self.__appversion

    @property
    def debug(self) -> bool:
        return self.__debug

    def set_environment(self, environment: RuntimeEnvironment) -> "Config":
        self.__environment = environment
        return self

    def set_app_name(self, appname: str) -> "Config":
        self.__appname = appname
        return self

    def set_app_version(self, appversion: str) -> "Config":
        self.__appversion = appversion
        return self

    def set_debug(self, debug: bool) -> "Config":
        self.__debug = debug
        return self

@Singleton()
class Zoe(metaclass=ZoeMeta):
    def __init__(self):
        self._config = Config()

    @property
    def configure(self) -> Config:
        return self._config

    @property
    def version(self) -> str:
        try:
            return version("zoe-framework")
        except PackageNotFoundError:
            return "dev"

    @property
    def environment(self) -> RuntimeEnvironment:
        return self._config.environment
    @property
    def appname(self) -> str:
        return self._config.appname
    @property
    def appversion(self) -> str:
        return self._config.appversion
    @property
    def debug(self) -> bool:
        return self._config.debug
