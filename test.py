import sys
import os
from types import ModuleType
from typing import Callable, TypeVar, ParamSpec, Any
from importlib.abc import PathEntryFinder, Loader
from importlib.machinery import FileFinder, SourceFileLoader
import importlib
from dataclasses import dataclass
from pyparsing import ParserElement, alphas, alphanums
import pyparsing as pp


@dataclass
class MacroCall:
    fn: str
    arg: str


class PyPreprocessor:
    CALL_SITE_PREFIX = "__macro_call__"

    def __init__(self):
        self.parser = self.build_parser()
        self.macro_calls = []

    def parse_macro_expr(self, loc: int, tokens: pp.ParseResults):
        macro_fn = str(tokens["fn"]).replace("!", "")

        call_idx = len(self.macro_calls)
        self.macro_calls.append(MacroCall(macro_fn, str(tokens["arg"])))

        return [f"{self.CALL_SITE_PREFIX}{call_idx}"]

    def build_parser(self) -> pp.ParserElement:
        ParserElement.set_default_whitespace_chars(" ")

        identifier = pp.Word(alphas + "_", alphanums + "_")
        macro_identifier = pp.Combine(
            identifier + pp.ZeroOrMore("." + identifier) + "!"
        )
        macro_expr = (
            macro_identifier.set_results_name("fn")
            + "("
            + pp.SkipTo(")").set_results_name("arg")
            + ")"
        )
        macro_expr.set_parse_action(self.parse_macro_expr)

        pym_src = (
            pp.StringStart()
            + pp.ZeroOrMore(pp.SkipTo(macro_expr) + macro_expr)
            + pp.SkipTo(pp.StringEnd())
        )

        return pym_src

    def preprocess_src(self, src: str) -> str:
        results = self.parser.parse_string(src)

        print("".join(results))


class MacroLoader(SourceFileLoader):
    preproc = PyPreprocessor()

    def __init__(self, fullname: str, path: str):
        super().__init__(fullname, path)
        self.path = path
        self.fullname = fullname

    def get_data(self, path) -> bytes:
        return super().get_data(path)

    def exec_module(self, module: ModuleType):
        src = self.get_data(self.path)
        src = self.preproc.preprocess_src(src.decode())

        try:
            exec(src, module.__dict__)
        except:
            raise ImportError(name=self.fullname, path=str(self.path))


class MacroImporter(PathEntryFinder):
    def __init__(self, path: str):
        self.search_path = path
        self.py_finder = FileFinder(path, (SourceFileLoader, [".py"]))
        self.macro_finder = FileFinder(path, (MacroLoader, [".pym"]))

    def find_spec(self, full_name: str, target=None):
        # .py take precedence over .pym
        mod_spec = self.py_finder.find_spec(full_name, target)
        if mod_spec:
            return mod_spec

        return self.macro_finder.find_spec(full_name, target)


def import_hook(path: str) -> Any:
    if not os.path.isdir(path):
        raise ImportError()
    decoded_path = str(path)
    print(decoded_path)
    return MacroImporter(path)


sys.path_hooks.insert(0, import_hook)
sys.path_importer_cache.clear()
importlib.invalidate_caches()

from io import StringIO
from pyml.elements import *
import time as ptime
import test1


def pymain():

    start = ptime.time()
    html_res = div(
        child=[div(child=[div() for i in range(1000)]) for i in range(1000)]
    )
    end = ptime.time()
    # print(html_res)
    print("Pyml time: ", end - start)

    start = ptime.time()
    with open("quick_test.html", "r", encoding="utf8") as f:
        html_res = f.read()
    end = ptime.time()
    # print(html_res)
    print("Opening file time: ", end - start)


# pymain()
