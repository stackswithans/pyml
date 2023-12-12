import sys
import os
from typing import Any
import importlib
from expan.importer import MacroImporter


def _import_hook(path: str) -> Any:
    if not os.path.isdir(path):
        raise ImportError()
    return MacroImporter(path)


sys.path_hooks.insert(0, _import_hook)
sys.path_importer_cache.clear()
importlib.invalidate_caches()
