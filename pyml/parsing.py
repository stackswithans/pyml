import expan
import pyparsing as pp
from typing import cast, Any
from pyparsing import alphas, alphanums, quoted_string, common
from pyparsing.results import ParseResults
import pyml.ast as pymlast
from pyml.ast import Element, Attribute, Node, Component


LBRACE, RBRACE = map(pp.Literal, "{}")
COLON = pp.Literal(":")

identifier = pp.Word(alphas + "_", alphanums + "_-")
expr = common.identifier ^ quoted_string ^ common.number
attribute = identifier("attr") + ":" + expr
attribute_list = pp.DelimitedList(
    attribute, delim=",", allow_trailing_delim=True
)
element = pp.Forward()
for_expr = pp.Forward()

# TODO: add python expressions
py_expr = common.identifier

child = element | for_expr | expr
children = pp.DelimitedList(child, delim=",")

for_expr <<= (
    pp.Keyword("for")
    + common.identifier("control_var")
    + pp.Keyword("in")
    + py_expr("iterable")
    + LBRACE
    + pp.Opt(children)("children")
    + RBRACE
)

element <<= (
    identifier("name")
    + LBRACE
    + pp.Opt(attribute_list)("attrs")
    + pp.Opt(children)("children")
    + RBRACE
)
# element_list = pp.DelimitedList(element | expr, delim=",")
pysx_parser = pp.StringStart() + children + pp.StringEnd()

# TODO: Add better error messages

# Component name must start with uppercase
@element.set_parse_action
def parse_element(loc: int, tokens: ParseResults) -> Node:
    ident: str = str(tokens["name"])
    if ident[0].isupper():
        props = {}
        attrs = list(cast(Any, tokens.get("attrs", [])))
        for attr in attrs:
            props[attr.attr] = attr.value

        props["children"] = pymlast.Siblings(
            list(cast(Any, tokens.get("children", [])))
        )
        return Component(ident, props)
    else:
        return Element(
            ident,
            list(cast(Any, tokens.get("attrs", []))),
            pymlast.Siblings(list(cast(Any, tokens.get("children", [])))),
        )


@attribute.set_parse_action
def parse_attribute(loc: int, tokens: ParseResults) -> Node:
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


@for_expr.set_parse_action
def parse_for_expr(loc: int, tokens: ParseResults) -> Node:
    print("parsed for")
    pass


@pysx_parser.set_parse_action
def parse_pysx(loc: int, tokens: ParseResults) -> Node:
    if len(tokens) == 1:
        return cast(Node, tokens[0])
    else:
        return pymlast.Siblings(list(tokens))
