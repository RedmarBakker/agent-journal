from functools import cache
from inspect import getmembers, isfunction


class StateSample:
    @classmethod
    # @sin EngineIndexOnUseDetector
    @cache
    def listeners(cls) -> tuple:
        return tuple(method for name, method in getmembers(cls, isfunction) if name.startswith("on_"))

    @classmethod
    def worked_out(cls) -> tuple:
        return tuple(method for name, method in getmembers(cls, isfunction) if name.startswith("on_"))
