import sys
import os
from typing import Any, cast
from dataclasses import dataclass
from pyparsing import ParserElement, alphas, alphanums
import pyparsing as pp
import builtins


@dataclass
class MacroCall:
    fn: str
    arg: str


class PyPreprocessor:
    CALL_SITE_PREFIX = "__macro_call__"
    parser: pp.ParserElement = cast(pp.ParserElement, None)

    def __init__(self):
        if PyPreprocessor.parser is None:
            PyPreprocessor.parser = self.build_parser()

        self.macro_calls = {}

    def parse_macro_expr(self, loc: int, tokens: pp.ParseResults):
        macro_fn = str(tokens["fn"]).replace("!", "")
        whitespace = "".join(tokens["whitespace"])

        call_key = f"{self.CALL_SITE_PREFIX}{len(self.macro_calls)}"
        self.macro_calls[call_key] = MacroCall(macro_fn, str(tokens["arg"]))
        return [f"{call_key}{whitespace}"]

    def build_parser(self) -> pp.ParserElement:
        identifier = pp.Word(alphas + "_", alphanums + "_")
        macro_identifier = pp.Combine(
            identifier + pp.ZeroOrMore("." + identifier) + "!"
        )

        # TODO: Account for other false positive scenarios
        expr_with_parens = pp.Char("(") + ... + ")"
        macro_expr = (
            macro_identifier.set_results_name("fn")
            + "("
            + pp.SkipTo(
                ")", include=True, ignore=expr_with_parens
            ).set_results_name("arg")
            + pp.White()[...].set_results_name("whitespace").leave_whitespace()
        )
        macro_expr.set_parse_action(self.parse_macro_expr)

        pym_src = (
            pp.StringStart()
            + pp.ZeroOrMore(pp.SkipTo(macro_expr, include=True))
            + pp.SkipTo(pp.StringEnd())
        )
        pym_src.set_whitespace_chars(" ")

        return pym_src

    def expand_macros(self, src: str, im_module_dict: dict) -> str:
        expanded_src = src
        for key, macro_call in self.macro_calls.items():
            try:
                macro_fn = eval(macro_call.fn, im_module_dict)
            except NameError as e:
                # TODO: Customize error message for when macro function not found
                raise e

            expand_result: str = macro_fn(macro_call.arg)
            expanded_src = expanded_src.replace(key, expand_result)
        return expanded_src

    def preprocess_src(self, src: str) -> str:
        processed_src = "".join(self.parser.parse_string(src))
        im_module_dict = dict(builtins.__dict__)
        im_module_dict.update({key: "" for key in self.macro_calls})
        exec(processed_src, im_module_dict)
        return self.expand_macros(processed_src, im_module_dict)
