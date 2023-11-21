import platform
import sys
import importlib
struct_ = importlib.import_module(".struct", package="smawe_tools")
try:
    from colorama import init as _init
    _init(autoreset=True)
except ModuleNotFoundError:
    pass

_IS_LESS_THEN_PY39 = float(".".join(platform.python_version_tuple()[:-1])) < 3.9
if _IS_LESS_THEN_PY39:
    import typing
    List = typing.List
else:
    List = list

# 'Linux', 'Darwin', 'Java', 'Windows'
OS_NAME = platform.system()


def modify_encoding(encoding="utf-8", language_code="en_US"):
    import _locale
    _locale._getdefaultlocale = lambda *args, **kwargs: (language_code, encoding)


sys.modules[__name__].__class__ = struct_.LoggingModule
