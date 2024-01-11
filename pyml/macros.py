import expan
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
    except pp.ParseSyntaxException as pe:
        print(pe.explain(), file=sys.stderr)
        raise Exception("Failed to parse macro")
    # pprint.pprint(root)
    buffer = StringIO()
    expander = Expander(root, buffer)
    py_str = expander.expand()
    # print(py_str)
    buffer.close()
    return py_str
