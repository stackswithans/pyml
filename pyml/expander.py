from io import StringIO
from typing import Callable, TypeVar, ClassVar, cast
from dataclasses import dataclass, field
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
    in_py_ctx: bool = False
    format_args: list[str] = field(default_factory=list)

    def _descend(self):
        self.depth += 1

    def _ascend(self):
        self.depth -= 1

    def _is_safe_str_for_f_str(self, string: str) -> bool:
        unsafe_char = ("{", "}")
        for c in unsafe_char:
            if c in string:
                return False
        return True

    def escape_expr(self, string: str) -> str:
        return self._get_format_idx(f"{string}")

    def escape_str(self, string: str, in_f_str: bool = True) -> str:
        if not self._is_safe_str_for_f_str(string) and in_f_str:
            return self._get_format_idx(f'"{string}"')

        # TODO: Escape HTML in strings
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
        if is_void and not node.children.is_empty():
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

    def _expand_children(self, children: pymlast.Siblings) -> str:
        child_buffer = StringIO()
        expander = Expander(children, child_buffer)
        rendered_child = expander.expand()
        return rendered_child

    def _expand_children_list(
        self, children: list[pymlast.Siblings], results: list[str] | None = None
    ) -> list[str]:
        if not results:
            results = []
        for child in children:
            child_buffer = StringIO()
            expander = Expander(child, child_buffer)
            results.append(expander.expand())
        return results

    def visit_component(self, node: pymlast.Component):
        buffer = StringIO()
        buffer.write(f"{node.name}(")
        children: pymlast.Siblings = cast(
            pymlast.Siblings, node.props["children"]
        )
        del node.props["children"]
        # TODO: handle props that aren't valid python identifiers
        for i, (prop, value) in enumerate(node.props.items()):
            value = cast(pymlast.Expr, value)
            val = value.eval(self, node)
            buffer.write(f"{prop}={val}")
            if i != len(node.props) - 1:
                buffer.write(", ")

        if not children.is_empty():
            rendered_child = self._expand_children(children)
            if len(node.props) > 0:
                buffer.write(", ")
            buffer.write(f"children={rendered_child}")

        buffer.write(f")")
        format_label = self._get_format_idx(buffer.getvalue())
        self.buffer.write(format_label)
        buffer.close()

    def _get_format_idx(self, format_arg: str) -> str:
        format_label = len(self.format_args)
        self.format_args.append(format_arg)
        # Escaped like this because of strings
        return f"{{{{{format_label}}}}}"

    def visit_attribute(self, node: pymlast.Attribute):
        val = node.value.eval(self, node)
        self.buffer.write(f" {node.attr}={val}")

    def visit_literal(self, node: pymlast.Literal):
        val = node.eval(self, node)
        self.buffer.write(f"{val}")

    def visit_name(self, node: pymlast.Name):
        self.buffer.write(f"{{{node.ident}}}")

    def visit_forexpr(self, node: pymlast.ForExpr):
        if node.children.is_empty():
            return
        rendered_child = self._expand_children(node.children)
        label = self._get_format_idx(
            f"''.join(({rendered_child} for {node.target} in {node.for_iter}))"
        )
        self.buffer.write(f"{label}")

    def _render_condition_branch(
        self, condition: str, block: pymlast.Siblings
    ) -> str:
        pass
        if block.is_empty():
            return f"({condition}, '')"
        else:
            rendered = self._expand_children(block)
            return f"({condition}, {rendered})"

    def visit_pyexpr(self, node: pymlast.PyExpr):
        label = self._get_format_idx(node.py_expr)
        self.buffer.write(f"{label}")

    def visit_if(self, node: pymlast.If):
        results = []
        if_branch = node.if_branch

        results.append(
            self._render_condition_branch(
                if_branch.condition, if_branch.children
            )
        )

        for elif_branch in node.elif_branches:
            results.append(
                self._render_condition_branch(
                    elif_branch.condition, elif_branch.children
                )
            )

        if node.else_block:
            results.append(
                self._render_condition_branch("True", node.else_block)
            )

        results_list = f"({', '.join(results)},)"

        # TODO: look for a better way to extract the list item
        label = self._get_format_idx(
            f"next(iter([render for cond, render in {results_list} if cond]), '')"
        )
        self.buffer.write(f"{label}")

    def expand(self) -> str:
        self.buffer.write(f"f{Expander.PY_STR_DELIM}")
        self.pyml.visit(self)
        self.buffer.write(f"{Expander.PY_STR_DELIM}")
        if self.format_args:
            format_args = ", ".join(self.format_args)
            self.buffer.write(f".format({format_args})")
        return self.buffer.getvalue()
