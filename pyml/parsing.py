import expan
import pyparsing as pp
from typing import cast, Any
from pyparsing import alphas, alphanums, quoted_string, common
from pyparsing.results import ParseResults
import pyml.ast as pymlast
from pyml.ast import Element, Attribute, Node


LBRACE, RBRACE = map(pp.Literal, "{}")
COLON = pp.Literal(":")

identifier = pp.Word(alphas + "_", alphanums + "_-")
# TODO: add python expressions
expr = common.identifier ^ quoted_string ^ common.number
attribute = identifier("attr") + ":" + expr
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
        pymlast.Siblings(list(cast(Any, tokens.get("children", [])))),
    )


@attribute.set_parse_action
def parse_attribute(loc: int, tokens: ParseResults) -> Node:
    print("Attribute parse: ", tokens)
    return Attribute(str(tokens["attr"]), cast(pymlast.Expr, tokens[2]))


@expr.set_parse_action
def parse_expr(loc: int, tokens: ParseResults) -> Node:
    tok: str | int | float = cast(str | int | float, tokens[0])
    if isinstance(tok, int) or isinstance(tok, float):
        return pymlast.Literal(pymlast.LiteralType.Number, tok)
    elif str(tok).startswith("'") or str(tok).startswith('"'):
        return pymlast.Literal(
            pymlast.LiteralType.String, tok[1 : len(tok) - 1]
        )
    else:
        return pymlast.Name(tok)


@pysx_parser.set_parse_action
def parse_pysx(loc: int, tokens: ParseResults) -> Node:
    if len(tokens) == 1:
        return cast(Node, tokens[0])
    else:
        return pymlast.Siblings(list(tokens))
