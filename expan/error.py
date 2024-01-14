from dataclasses import dataclass
from typing import ClassVar
from functools import reduce
import termcolor
import pyparsing


def _get_len_largest_line(lines: list[str]) -> int:
    return max(map(lambda x: len(x), lines))


@dataclass
class ExpansionError(Exception):
    message: str
    line: int = -1
    col: int = -1
    detail: str = ""
    default_err_header: ClassVar[str] = "Error while performing macro expansion"

    def explain(self, message: str = "") -> str:
        if not message:
            message = ExpansionError.default_err_header
        return (
            f"{message}:\n{self.detail}"
            if self.detail
            else "{message}:\n{self.message}"
        )

    def add_detail(
        self,
        original_src: str,
        loc: int,
        src_path: str,
        macro_fn: str,
        macro_args: str,
    ):
        macro_lineno = pyparsing.lineno(loc, original_src)
        macro_col = pyparsing.col(loc, original_src)
        # Add error marker to line
        arg_lines = macro_args.split("\n")
        ident_spaces = "    "
        marker_col = (
            len(ident_spaces)
            + len(macro_fn)
            + (self.col - 1)
            + 2  # takes '!' and '(' into account
            if self.line == 1
            else (self.col - 1)
        )

        err_marker = termcolor.colored("-" * marker_col + "^\n\n", "red")
        arg_lines.insert(self.line, err_marker)
        macro_args = "\n".join(arg_lines)
        detail_delim = "-" * _get_len_largest_line(arg_lines)

        msg = termcolor.colored(self.message, "red")

        header = termcolor.colored(
            f"{src_path}, macro call located at (line {macro_lineno}: col {macro_col})",
            "red",
        )
        self.detail = f"""\
{header}
{ident_spaces}{macro_fn}!({macro_args})
\n{detail_delim}\n
{msg}
"""

    def __str__(self) -> str:
        return self.detail
