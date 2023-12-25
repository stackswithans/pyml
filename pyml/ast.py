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


@dataclass
class Node:
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
    def eval(self) -> Any:
        ...


@dataclass
class Attribute(Node):
    attr: str
    value: Expr


@dataclass
class Literal(Node, Expr):
    lit_type: LiteralType
    value: str | int | float

    def eval(self) -> Any:
        return self.value


@dataclass
class Name(Node, Expr):
    ident: str

    def eval(self) -> Any:
        return f"{{{self.ident}}}"


@dataclass
class Element(Node):
    name: str
    attrs: list[Attribute]
    children: Siblings


@dataclass
class Component(Node):
    name: str
    props: dict[str, Expr]
