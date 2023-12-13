import expan
import pyparsing as pp
from dataclasses import dataclass
from typing import cast, Any
from pyparsing import alphas, alphanums, quoted_string, ParserElement, common
from pyparsing.results import ParseResults
import pyml.ast as pymlast
from pyml.ast import Element, Attribute, Node
import pprint


LBRACE, RBRACE = map(pp.Literal, "{}")
COLON = pp.Literal(":")

identifier = pp.Word(alphas + "_", alphanums + "_-")

# TODO: add python expressions
expr = common.identifier ^ quoted_string ^ common.number

attribute = identifier("attr") + ":" + expr("value")

attribute_list = pp.DelimitedList(
    attribute, delim=",", allow_trailing_delim=True
)


element = pp.Forward()
child = expr ^ element
children = pp.DelimitedList(child, delim=",")

element <<= (
    identifier("name")
    + LBRACE
    + pp.Opt(attribute_list)("attrs")
    + pp.Opt(children)("children")
    + RBRACE
)
element_list = pp.DelimitedList(element, delim=",")

pysx_parser = pp.StringStart() + element_list + pp.StringEnd()


@element.set_parse_action
def parse_element(loc: int, tokens: ParseResults) -> Node:
    return Element(
        str(tokens["name"]),
        list(cast(Any, tokens.get("attrs", []))),
        list(cast(Any, tokens.get("children", []))),
    )


@attribute.set_parse_action
def parse_attribute(loc: int, tokens: ParseResults) -> Node:
    return Attribute(str(tokens["attr"]), cast(pymlast.Expr, tokens["value"]))


@expr.set_parse_action
def parse_expr(loc: int, tokens: ParseResults) -> Node:
    tok: str | int = cast(str | int, tokens[0])
    if isinstance(tok, int):
        return pymlast.Literal(pymlast.LiteralType.Number, tok)
    elif str(tok).startswith("'") or str(tok).startswith('"'):
        return pymlast.Literal(pymlast.LiteralType.String, tok)
    else:
        return pymlast.Name(tok)


@expan.expr_macro
def pyml(arg: str) -> str:
    result = pysx_parser.parse_string(arg, True)

    pprint.pprint(result)
    return "'Hello world'"
