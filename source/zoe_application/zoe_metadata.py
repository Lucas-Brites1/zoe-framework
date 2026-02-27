from importlib.metadata import version, PackageNotFoundError
from enum import Enum


class ZoeMetadata:
    __debug: bool = False

    @staticmethod
    def enable_debug() -> None:
        ZoeMetadata.__debug = True

    @staticmethod
    def is_debug() -> bool:
        return ZoeMetadata.__debug

    @staticmethod
    def version() -> str:
        try:
            version("zoe-framework")
        except PackageNotFoundError:
            return "dev"
    
    @staticmethod
    def framework() -> str:
        return "zoe-framework"