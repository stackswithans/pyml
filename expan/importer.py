import sys
from types import ModuleType
from importlib.abc import PathEntryFinder
from importlib.machinery import FileFinder, SourceFileLoader
from expan.preprocessor import PyPreprocessor
from expan.error import ExpansionError


class MacroLoader(SourceFileLoader):
    def __init__(self, fullname: str, path: str):
        super().__init__(fullname, path)
        self.path = path
        self.fullname = fullname
        self.preproc = PyPreprocessor()

    def get_data(self, path) -> bytes:
        return super().get_data(path)

    def exec_module(self, module: ModuleType):

        src = self.get_data(self.path)
        try:
            src = self.preproc.preprocess_src(str(self.path), src.decode())
            exec(src, module.__dict__)
        except ExpansionError as e:
            print(e.detail, file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            raise ImportError(name=self.fullname, path=str(self.path)) from e


class MacroImporter(PathEntryFinder):
    def __init__(self, path: str):
        self.search_path = path
        self.macro_finder = FileFinder(path, (MacroLoader, [".pyxp"]))

    def find_spec(self, full_name: str, target=None):
        # .py takes precedence over .pym
        # Ignore 'self' import hook
        for hook in sys.path_hooks[1:]:
            try:
                finder = hook(self.search_path)
            except ImportError:
                continue
            mod_spec = finder.find_spec(full_name, target)
            if mod_spec:
                return mod_spec

        return self.macro_finder.find_spec(full_name, target)
