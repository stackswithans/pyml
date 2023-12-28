import expan
import traceback as tb
import pyparsing as pp
from typing import cast, Any
from pyparsing import alphas, alphanums, quoted_string, common
from pyparsing.results import ParseResults
import pyml.ast as pymlast
from pyml.ast import Element, Attribute, Node, Component
import ast


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
py_ident = common.identifier
py_expr = common.identifier

#########Python grammar section################################
"""
t_lookahead = pp.Char('(') | '[' | '.'

no_match_lookahead = pp.NotAny(t_lookahead)
match_lookahead = pp.FollowedBy(t_lookahead)

t_primary = pp.Forward()

t_primary <<= t_primary + '.'+ py_ident + match_lookahead\
    | t_primary + '[' +  slices +  ']' +  match_lookahead\
    | t_primary +  genexp +  match_lookahead\
    | t_primary + '(' +  pp.Opt(arguments) + ')' + match_lookahead\
    | atom + match_lookahead

single_target:
    | single_subscript_attribute_target
    | NAME 
    | '(' single_target ')' 
single_subscript_attribute_target:
    | t_primary '.' NAME !t_lookahead 
    | t_primary '[' slices ']' !t_lookahead 

del_targets: ','.del_target+ [','] 
del_target:
    | t_primary '.' NAME !t_lookahead 
    | t_primary '[' slices ']' !t_lookahead 
    | del_t_atom
del_t_atom:
    | NAME 
    | '(' del_target ')' 
    | '(' [del_targets] ')' 
    | '[' [del_targets] ']' 

star_target = pp.Forward()

target_with_star_atom = pp.Forward()

star_targets_list_seq = pp.DelimitedList(
    star_target, delim=",", allow_trailing_delim=True
)

star_targets_tuple_seq = (
    star_target + pp.OneOrMore(pp.Group("," + star_target)) + pp.Opt(",")
    | star_target + ","
)

star_atom = (
    py_ident
    | "(" + target_with_star_atom + ")"
    | "(" + pp.Opt(star_targets_tuple_seq) + ")"
    | "[" + pp.Opt(star_targets_list_seq) + "]"
)

target_with_star_atom <<= (
    (t_primary + pp.Char(".") + no_match_lookahead)
    | (t_primary + "[" + slices + "]" + no_match_lookahead)
    | star_atom
)


star_target <<= (
    pp.Char("*") + pp.Group(pp.NotAny("*") + star_target)
) | target_with_star_atom

star_targets = star_target + pp.NotAny(",") | pp.Opt(
    pp.DelimitedList(star_target, delim=",")
)
"""
###############################################################
child = element | for_expr | expr

children = pp.DelimitedList(child, delim=",")

for_expr <<= (
    pp.Keyword("for")
    + pp.SkipTo(pp.Keyword("in"))("target")
    + pp.Keyword("in")
    + pp.SkipTo(LBRACE)("iter")
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
    target = tokens["target"]
    for_iter = tokens["iter"]

    py_for = f"for {target} in {for_iter}:\n\tpass"

    try:
        ast.parse(py_for)
    except SyntaxError as e:
        raise pp.ParseFatalException(
            f"Error while parsing for expression:\n{tb.format_exc()}"
        )
    print(py_for)


@pysx_parser.set_parse_action
def parse_pysx(loc: int, tokens: ParseResults) -> Node:
    if len(tokens) == 1:
        return cast(Node, tokens[0])
    else:
        return pymlast.Siblings(list(tokens))
