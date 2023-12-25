import pytest
import time
from lxml import etree
from pyml.macros import pysx

@pytest.fixture
def test_elements_page() -> bytes:
    with open("tests/pages/test_elements.html", "r", encoding="utf8") as f:
        return etree.tostring(etree.HTML(f.read()), pretty_print=True)


def test_elements_render_correctly(test_elements_page: str):
    page = f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><meta name='generator' content='Docutils 0.17.1: http://docutils.sourceforge.net/'><title>builtins — Built-in objects &#8212; Python 3.10.13 documentation</title><link rel='stylesheet' href='../_static/pygments.css' type='text/css'><script id='documentation_options' src='../_static/documentation_options.js' data-url_root='../'></script><style>{{0}}</style></head><body></body></html>".format("@media only screen {table.full-width-table {width: 100%;}}")

    assert (
        etree.tostring(etree.HTML(page), pretty_print=True)
        == test_elements_page
    )
