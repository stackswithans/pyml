import expan
import pyparsing as pp
from pyparsing import alphas, alphanums, quoted_string, ParserElement


LBRACE, RBRACE = map(pp.Literal, "{}")
COLON = pp.Literal(":")

identifier = pp.Word(alphas + "_", alphanums + "_-")


attribute = (
    identifier.set_results_name("attr")
    + ":"
    + quoted_string.set_results_name("value")
)
attribute_list = pp.DelimitedList(
    attribute, delim=",", allow_trailing_delim=True
)


element = pp.Forward()
child = quoted_string | element
children = pp.DelimitedList(child, delim=",")

element <<= (
    identifier + LBRACE + pp.Opt(attribute_list) + pp.Opt(children) + RBRACE
)
element_list = pp.DelimitedList(element, delim=",")

pysx_parser = pp.StringStart() + element_list + pp.StringEnd()


@expan.expr_macro
def pyml(arg: str) -> str:
    result = pysx_parser.parse_string(arg, True)

    print(result)
    return "'Hello world'"
