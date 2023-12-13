from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import pprint


class LiteralType(Enum):
    Number = 0
    String = 1


@dataclass
class Node:
    def __str__(self) -> str:
        return pprint.pformat(self)


@dataclass
class Expr(Node):
    pass


@dataclass
class Attribute(Node):
    attr: str
    value: Expr


@dataclass
class Literal(Expr):
    lit_type: LiteralType
    value: str | int


@dataclass
class Name(Expr):
    ident: str


@dataclass
class Element(Node):
    name: str
    attrs: list[Attribute]
    children: list[Expr | Element]
