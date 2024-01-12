from dataclasses import dataclass
import pyparsing


@dataclass
class ExpansionError(Exception):
    detail: str
    line: int = -1
    col: int = 1

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
Error while performing macro expansion: 
{src_path} ({macro_lineno}:{macro_col})
    {macro_fn}!({macro_args})
Details: 
{str(err)}
"""
