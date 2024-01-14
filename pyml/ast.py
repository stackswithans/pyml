from __future__ import annotations
from typing import Protocol, Any, runtime_checkable
from dataclasses import dataclass
from enum import Enum
import pprint


class LiteralType(Enum):
    Number = 0
    String = 1


class Visitor(Protocol):
    def visit_siblings(self, node: Siblings):
        ...

    def visit_element(self, node: Element):
        ...

    def visit_component(self, node: Component):
        ...

    def visit_attribute(self, node: Attribute):
        ...

    def visit_literal(self, node: Literal):
        ...

    def visit_name(self, node: Name):
        ...

    def visit_forexpr(self, node: ForExpr):
        ...

    def visit_if(self, node: If):
        ...

    def visit_pyexpr(self, node: PyExpr):
        ...

    def escape_str(self, string: str, in_f_str: bool = True) -> str:
        ...

    def escape_expr(self, string: str) -> str:
        ...


@dataclass
class Node:
    src: str
    loc: int

    def visit(self, visitor: Visitor):
        cls_name = self.__class__.__name__

        visitor_fn = getattr(visitor, f"visit_{cls_name.lower()}", None)
        if not visitor_fn:
            raise NotImplementedError(
                f"Visitor method not found for node type: {cls_name}"
            )
        visitor_fn(self)

    def __str__(self) -> str:
        return pprint.pformat(self)


@dataclass
class Siblings(Node):
    children: list[Node]

    def is_empty(self) -> bool:
        return len(self.children) == 0


@runtime_checkable
@dataclass
class Expr(Protocol):
    def eval(self, visitor: Visitor, ctx: Node) -> Any:
        ...


# TODO: Handle html in attribute values
@dataclass
class Attribute(Node):
    attr: str
    value: Expr


@dataclass
class Literal(Node, Expr):
    lit_type: LiteralType
    value: str | int | float

    # TODO: Escape HTML in string literals
    def eval(self, visitor: Visitor, ctx: Node) -> Any:
        match ctx:
            case Attribute():
                if self.lit_type == LiteralType.String:
                    safe_str = visitor.escape_str(str(self.value))
                    return f"'{safe_str}'"
                else:
                    return f"'{self.value}'"
            case Literal():
                if self.lit_type == LiteralType.String:
                    safe_str = visitor.escape_str(str(self.value))
                    return f"{safe_str}"
                else:
                    return f"{self.value}"
            case Component():
                safe_str = visitor.escape_str(str(self.value), False)
                return (
                    f'"{visitor.escape_str(safe_str)}"'
                    if self.lit_type == LiteralType.String
                    else f"{self.value}"
                )
            case _:
                raise NotImplementedError(
                    f"Unhandled eval node type: {ctx.__class__.__name__}"
                )


@dataclass
class Name(Node, Expr):
    ident: str

    def eval(self, visitor: Visitor, ctx: Node) -> Any:
        match ctx:
            case Attribute():
                return f"'{{{self.ident}}}'"
            case Component():
                return self.ident
            case _:
                raise NotImplementedError(
                    f"Unhandled eval node type: {ctx.__class__.__name__}"
                )


@dataclass
class Element(Node):
    name: str
    attrs: list[Attribute]
    children: Siblings


@dataclass
class ForExpr(Node):
    target: str
    for_iter: str
    children: Siblings


@dataclass
class CondBranch(Node):
    condition: str
    children: Siblings


@dataclass
class If(Node):
    if_branch: CondBranch
    elif_branches: tuple[CondBranch]
    else_block: Siblings | None


@dataclass
class PyExpr(Node, Expr):
    py_expr: str

    def eval(self, visitor: Visitor, ctx: Node) -> Any:
        match ctx:
            case Attribute():
                safe_str = visitor.escape_expr(self.py_expr)
                return f"'{safe_str}'"
            case Component():
                return f"{self.py_expr}"
            case _:
                raise NotImplementedError(
                    f"Unhandled eval node type: {ctx.__class__.__name__}"
                )


# TODO: Handle HTML in props
@dataclass
class Component(Node):
    name: str
    props: dict[str, Node]
