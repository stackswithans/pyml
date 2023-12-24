from io import StringIO
from typing import Callable, TypeVar, ClassVar
from dataclasses import dataclass
import pyml.ast as pymlast
import pyml.elements as elements

T = TypeVar("T")


VisitFn = Callable[["Expander", T], None]


@dataclass
class Expander(pymlast.Visitor):
    PY_STR_DELIM: ClassVar[str] = '"'

    pyml: pymlast.Node
    buffer: StringIO
    depth: int = 0

    def _descend(self):
        self.depth += 1

    def _ascend(self):
        self.depth -= 1

    def _escape_str(self, string: str) -> str:
        buf = StringIO()
        for i, char in enumerate(string):
            prev_char = string[i - 1] if i > 0 else char

            if char == Expander.PY_STR_DELIM and prev_char != "\\":
                buf.write("\\")
            buf.write(char)
        val = buf.getvalue()
        buf.close()
        return val

    def visit_siblings(self, node: pymlast.Siblings):
        for el in node.children:
            el.visit(self)

    def visit_element(self, node: pymlast.Element):
        builder_ty = elements.get_builder(node.name)
        if not builder_ty:
            raise Exception("Invalid element used!!!")
        is_void = builder_ty == elements.ElementBuilderType.Void
        if is_void and node.children:
            raise Exception(f"Void element {node.name} cannot have children!!!")

        self.buffer.write(f"<{node.name}")

        for attr in node.attrs:
            attr.visit(self)
        self.buffer.write(f">")

        if is_void:
            return
        self._ascend()
        node.children.visit(self)
        self._descend()

        self.buffer.write(f"</{node.name}>")

    def visit_attribute(self, node: pymlast.Attribute):
        match node.value:
            case pymlast.Name():
                self.buffer.write(f" {node.attr}='{node.value.eval()}'")
            case pymlast.Expr():
                raw_val = node.value.eval()
                if isinstance(raw_val, str):
                    value = self._escape_str(node.value.eval())
                else:
                    value = f"{raw_val}"
                self.buffer.write(f" {node.attr}='{value}'")
            case _:
                raise NotImplementedError("New node expression type")

    def visit_literal(self, node: pymlast.Literal):
        raw_val = node.eval()
        if isinstance(raw_val, str):
            self.buffer.write(f" {self._escape_str(raw_val)} ")
        else:
            self.buffer.write(f" {raw_val} ")

    def visit_name(self, node: pymlast.Name):
        self.buffer.write(f" {{{node.ident}}} ")

    def expand(self) -> str:
        self.buffer.write(f"f{Expander.PY_STR_DELIM}")
        self.pyml.visit(self)
        self.buffer.write('"')
        return self.buffer.getvalue()
