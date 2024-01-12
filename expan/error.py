from dataclasses import dataclass
from typing import ClassVar
import pyparsing


@dataclass
class ExpansionError(Exception):
    detail: str
    line: int = -1
    col: int = 1
    default_err_header: ClassVar[str] = "Error while performing macro expansion"

    def explain(self, message: str = "") -> str:
        if not message:
            message = ExpansionError.default_err_header
        return f"{message}:\n{self.detail}"

    def __str__(self) -> str:
        return self.detail


def format_expansion_err(
    original_src: str,
    loc: int,
    src_path: str,
    macro_fn: str,
    macro_args: str,
    err: ExpansionError,
) -> str:
    macro_line = pyparsing.line(loc, original_src)
    macro_lineno = pyparsing.lineno(loc, original_src)
    macro_col = pyparsing.col(loc, original_src)
    return f"""\
{src_path} ({macro_lineno}:{macro_col})
    {macro_fn}!({macro_args})
Details: 
{str(err)}
"""
