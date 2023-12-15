import expan
import pprint
import pyml.parsing as pymlparsing
from io import StringIO
from typing import cast
from pyml.ast import Node


@expan.expr_macro
def pysx(arg: str) -> str:
    # TODO: Handle syntax errors
    root: Node = cast(Node, pymlparsing.pysx_parser.parse_string(arg, True)[0])
    pprint.pprint(root)
    buffer = StringIO()
    pprint.pprint(buffer.getvalue())
    buffer.close()
    return "'Hello world'"
