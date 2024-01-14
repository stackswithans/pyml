import expan
from expan.error import ExpansionError
import pprint
import pyparsing as pp
import pyml.parsing as pymlparsing
import sys
from io import StringIO
from typing import cast
from pyml.ast import Node
from pyml.expander import Expander


@expan.expr_macro
def pysx(arg: str) -> str:
    # TODO: Handle syntax errors
    try:
        root: Node = cast(
            Node, pymlparsing.pysx_parser.parse_string(arg, True)[0]
        )
        buffer = StringIO()
        expander = Expander(root, buffer)
        py_str = expander.expand()
        # print(py_str)
        buffer.close()
        return py_str
    except Exception as e:
        match e:
            case pp.ParseException() | pp.ParseFatalException():
                raise ExpansionError(str(e), e.lineno, e.col)
            case _:
                raise e
