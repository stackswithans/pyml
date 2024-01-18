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

py_ident = common.identifier + pp.NotAny(LBRACE)

identifier = pp.Word(alphas + "_", alphanums + "_-")

py_helper = (
    pp.Keyword("py")
    - LBRACE
    - pp.SkipTo(RBRACE, ignore=quoted_string)("py_expr")
    + RBRACE
)

expr = py_helper | py_ident | quoted_string | common.number

attribute = identifier("attr") + ":" - expr
attribute_list = pp.DelimitedList(
    attribute, delim=",", allow_trailing_delim=True
)

element = pp.Forward()
for_expr = pp.Forward()
if_stmt = pp.Forward()
elif_stmt = pp.Forward()
else_block = pp.Forward()

child = expr ^ element ^ for_expr ^ if_stmt

children = pp.DelimitedList(child, delim=",")

for_expr <<= (
    pp.Keyword("for")
    - pp.SkipTo(pp.Keyword("in"))("target")
    - pp.Keyword("in")
    - pp.SkipTo(LBRACE)("iter")
    - LBRACE
    - pp.Opt(children)("children")
    - RBRACE
)

conditional_branch = (
    pp.SkipTo(LBRACE)("condition")
    - LBRACE
    - pp.Opt(children)("children")
    - RBRACE
)

if_stmt <<= (
    pp.Keyword("if")
    - conditional_branch  # TODO: Report this bug:  Parse action not called when set_results_name is used with this parse element
    - pp.ZeroOrMore(elif_stmt)("elif_branches")
    - pp.Opt(else_block)("else_block")
)

elif_stmt <<= pp.Keyword("elif") - conditional_branch

else_block <<= (
    pp.Keyword("else") - LBRACE - pp.Opt(children)("children") - RBRACE
)


element <<= (
    identifier("name")
    + LBRACE
    - pp.Opt(attribute_list)("attrs")
    - pp.Opt(children)("children")
    - RBRACE
)

top_level_str = quoted_string("top_level_str")
element_list = pp.DelimitedList(element ^ top_level_str, delim=",")
pysx_parser = pp.StringStart() - element_list - pp.StringEnd()

# TODO: Add better error messages

# Component name must start with uppercase
@element.set_parse_action
def parse_element(s: str, loc: int, tokens: ParseResults) -> Node:
    ident: str = str(tokens["name"])
    if ident[0].isupper():
        props = {}
        attrs = list(cast(Any, tokens.get("attrs", [])))
        for attr in attrs:
            props[attr.attr] = attr.value

        props["children"] = pymlast.Siblings(
            s, loc, list(cast(Any, tokens.get("children", [])))
        )
        return Component(s, loc, ident, props)
    else:
        return Element(
            s,
            loc,
            ident,
            list(cast(Any, tokens.get("attrs", []))),
            pymlast.Siblings(
                s, loc, list(cast(Any, tokens.get("children", [])))
            ),
        )


@attribute.set_parse_action
def parse_attribute(s: str, loc: int, tokens: ParseResults) -> Node:
    return Attribute(s, loc, str(tokens["attr"]), cast(pymlast.Expr, tokens[2]))


@top_level_str.set_parse_action
def parse_str(s: str, loc: int, tokens: ParseResults) -> Node:
    tok = str(tokens[0])
    return pymlast.Literal(
        s, loc, pymlast.LiteralType.String, tok[1 : len(tok) - 1]
    )


@expr.set_parse_action
def parse_expr(s: str, loc: int, tokens: ParseResults) -> Node:
    tok = cast(str | int | float | pymlast.PyExpr, tokens[0])
    if isinstance(tok, pymlast.PyExpr):
        return tok
    elif isinstance(tok, int) or isinstance(tok, float):
        return pymlast.Literal(s, loc, pymlast.LiteralType.Number, tok)
    elif str(tok).startswith("'") or str(tok).startswith('"'):
        return pymlast.Literal(
            s, loc, pymlast.LiteralType.String, tok[1 : len(tok) - 1]
        )
    else:
        return pymlast.Name(s, loc, tok)


@for_expr.set_parse_action
def parse_for_expr(s: str, loc: int, tokens: ParseResults) -> Node:
    target = str(tokens["target"])
    for_iter = str(tokens["iter"])
    # Parse for expression as a for statement
    py_for = f"for {target} in {for_iter}:\n\tpass"
    try:
        ast.parse(py_for)
    except SyntaxError:
        raise pp.ParseFatalException(
            f"Error while parsing for expression:\n{tb.format_exc()}"
        )

    return pymlast.ForExpr(
        s,
        loc,
        target,
        for_iter,
        pymlast.Siblings(s, loc, list(cast(Any, tokens.get("children", [])))),
    )


@conditional_branch.set_parse_action
def parse_conditional_branch(s: str, loc: int, tokens: ParseResults) -> Node:
    condition = str(tokens["condition"])
    try:
        ast.parse("if {condition}:\n\tpass")
    except SyntaxError:
        raise pp.ParseFatalException(
            f"Error while parsing if helper:\n{tb.format_exc()}"
        )
    return pymlast.CondBranch(
        s,
        loc,
        condition.strip(),
        pymlast.Siblings(s, loc, list(cast(Any, tokens.get("children", [])))),
    )


@else_block.set_parse_action
def parse_else_block(s: str, loc: int, tokens: ParseResults) -> Node:
    return pymlast.Siblings(s, loc, list(cast(Any, tokens.get("children", []))))


@elif_stmt.set_parse_action
def parse_elif_stmt(s: str, loc: int, tokens: ParseResults) -> Node:
    return cast(pymlast.CondBranch, tokens[1])


def _is_py_expr(node: ast.Module) -> bool:
    stmts = node.body
    if not stmts or len(stmts) == 0 or len(stmts) > 1:
        return False

    return isinstance(stmts[0], ast.Expr)


@py_helper.set_parse_action
def parse_py_helper(s: str, loc: int, tokens: ParseResults) -> Node:
    py_expr = str(tokens["py_expr"])

    try:
        node = ast.parse(py_expr)
        if not _is_py_expr(node):
            raise SyntaxError
    except SyntaxError:
        raise pp.ParseFatalException(
            f"Error while parsing if helper:\n{tb.format_exc()}"
        )
    return pymlast.PyExpr(s, loc, py_expr)


@if_stmt.set_parse_action
def parse_if_stmt(s: str, loc: int, tokens: ParseResults) -> Node:
    if_branch = cast(pymlast.CondBranch, tokens[1])
    elif_branches = cast(
        tuple[pymlast.CondBranch], tuple(tokens["elif_branches"])
    )
    else_block = cast(pymlast.Siblings | None, tokens.get("else_block"))
    return pymlast.If(s, loc, if_branch, elif_branches, else_block)


@pysx_parser.set_parse_action
def parse_pysx(s: str, loc: int, tokens: ParseResults) -> Node:
    if len(tokens) == 1:
        return cast(Node, tokens[0])
    else:
        return pymlast.Siblings(s, loc, list(tokens))
