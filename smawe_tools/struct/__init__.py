from types import ModuleType
import logging
import sys


class LoggingModule(ModuleType):

    _name = "smawe_tools.settings"

    def __getattr__(self, name):
        if "__getattr__" in sys.modules["__main__"].__dict__:
            r = sys.modules["__main__"].__dict__["__getattr__"](name)
            if not r:
                raise AttributeError(f"module {type(self)._name!r} has no attribute {name!r}")
            return r
        raise AttributeError(f"module {type(self)._name!r} has no attribute {name!r}")

    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)

    def __setattr__(self, attr, value):
        if attr == "ENABLED_LOG":
            if value:
                logging.basicConfig(format="%(asctime)s:%(filename)s:%(threadName)s:%(levelname)s:%(message)s",
                                    level=logging.INFO)
        super().__setattr__(attr, value)
