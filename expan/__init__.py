import sys
import os
from typing import Any, Callable
import importlib
from expan.importer import MacroImporter


Macro = Callable[[str], str]


def expr_macro(macro: Macro) -> Macro:
    def macro_decorator(arg: str) -> str:
        result = macro(arg)
        if not result:
            raise TypeError("Macro must return a non-empty string")

        return result

    return macro_decorator


def _import_hook(path: str) -> Any:
    if not os.path.isdir(path):
        raise ImportError()
    return MacroImporter(path)


sys.path_hooks.insert(0, _import_hook)
sys.path_importer_cache.clear()
importlib.invalidate_caches()
