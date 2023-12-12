from typing import Any
from macropy.core.macros import Macros  # type: ignore
from macropy.core import real_repr, unparse  # type: ignore


macros = Macros()


@macros.expr  # type: ignore
def pyml(tree: Any, **kw: Any):
    print(tree)
    print(real_repr(tree))
    print(unparse(tree))  # type: ignore
    return tree
