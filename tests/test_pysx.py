import pytest
import time
from lxml import etree
from pyml.macros import pysx

from pyml.macros import pysx
from pyml.component import component, Props
import sys
import os
from typing import Callable, TypeVar, ParamSpec, Any
from dataclasses import dataclass
from io import StringIO

@component
def Scaffold(props: Props):
    children = props.children 
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width' initial-scale='1'></head><body>{children}</body></html>"

def str_to_etree(html: str) -> bytes: 
    return etree.tostring(etree.HTML(html), pretty_print=True)

@pytest.fixture
def test_elements_page() -> bytes:
    with open("tests/pages/test_elements.html", "r", encoding="utf8") as f:
        return etree.tostring(etree.HTML(f.read()), pretty_print=True)


def test_elements_render_correctly(test_elements_page: str):
    page = f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><meta name='generator' content='Docutils 0.17.1: http://docutils.sourceforge.net/'><title>builtins — Built-in objects &#8212; Python 3.10.13 documentation</title><link rel='stylesheet' href='../_static/pygments.css' type='text/css'><script id='documentation_options' src='../_static/documentation_options.js' data-url_root='../'></script><style>{{0}}</style></head><body></body></html>".format("@media only screen {table.full-width-table {width: 100%;}}")

    assert str_to_etree(page)== test_elements_page

def test_component_renders_correctly():
    attr_2 = "hello world"
    value = 0
    page = f"{{0}}".format(Scaffold(testeProp=1, children=f"<div attr-1='red' attr-2='{attr_2}' attr-3='0'>{value}<div>Taki</div></div><div>teste1</div><div>teste2</div><ol></ol>"))

    assert str_to_etree(page) == str_to_etree(f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width' initial-scale='1'></head><body><div attr-1='red' attr-2='hello world' attr-3='0'>0<div>Taki</div></div><div>teste1</div><div>teste2</div><ol></ol></body></html>")


def test_for_expression():
    word_list = ["hello world", "bye world"]
    page = f"<div><h1>List content</h1>{{0}}</div>".format(''.join((f"<b>{word}</b>" for word  in word_list )))

    assert str_to_etree(page) == str_to_etree(f"<div><h1>List content</h1><b>hello world</b><b>bye world</b></div>")

def test_complex_for_expression():
    word_list = ["hello world", "bye world"]
    page = f"<div><h1>List content</h1>{{0}}</div>".format(''.join((f"<b>{i}</b><b>{word}</b>" for i, word  in enumerate(word_list) )))

    assert str_to_etree(page) == str_to_etree(f"<div><h1>List content</h1><b>0</b><b>hello world</b><b>1</b><b>bye world</b></div>")

def test_if_helper():
    is_visible = True
    page = f"<div><h1>Testing if</h1>{{0}}{{1}}</div>".format(next(iter([render for cond, render in ((is_visible, f"hello world"),) if cond]), ''), next(iter([render for cond, render in ((not is_visible, f"bye world"), (True, f" still hello world"),) if cond]), ''))

    assert str_to_etree(page) == str_to_etree(f"<div><h1>Testing if</h1>hello world still hello world</div>")

def test_if_elif_helper():
    lit_type = "string"
    page = f"<div><h1>Testing if</h1>{{0}}</div>".format(next(iter([render for cond, render in ((lit_type == "list_lit", f"[]"), (lit_type == "float", f"3.14"), (lit_type == "string", f"Hello world"), (True, f"unknown type"),) if cond]), ''))

    assert str_to_etree(page) == str_to_etree(f"<div><h1>Testing if</h1>Hello world</div>")

def test_py_helper():
    @component
    def Test(props: Props): 
        return f"<h1>{{0}}</h1>".format(props.prop1 )

    lit_type = "string"
    page = f"<div><h1 attr-1='{{0}}'>{{1}}</h1>{{2}}</div>".format("i am attribute" , ",".join(str(i) for i in [1, 2, 3, 4]) , Test(prop1="i am prop"))
    assert str_to_etree(page) == str_to_etree(f"<div><h1 attr-1='i am attribute'>1,2,3,4</h1><h1>i am prop</h1></div>")
