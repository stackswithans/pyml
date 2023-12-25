from pyml.macros import pysx
from pyml.component import component, Props
import sys
import os
from typing import Callable, TypeVar, ParamSpec, Any
from dataclasses import dataclass
from io import StringIO


def stringify(source: str) -> str:
    formatted_src = source.replace("\n", "\\n")
    return f"'{formatted_src}'"


@component
def Scaffold(props: Props):
    children = props.children
    return f" <!DOCTYPE html> <head><meta charset='utf-8'><meta name='viewport' content='width=device-width' initial-scale='1'></head><body> {children} </body>"


def pymain():
    value = "Hello marco"
    attr_2 = "blue"
    print(
        f"{{0}}".format(
            Scaffold(
                testeProp=1,
                children=f"<div attr-1='red' attr-2='{attr_2}' attr-3='0'> {value} <div> Taki </div></div><div> teste1 </div><div> teste2 </div><ol></ol>",
            )
        )
    )
