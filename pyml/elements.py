from __future__ import annotations
from io import StringIO
from typing import (
    Any,
    TypeAlias,
    Mapping,
    Protocol,
    runtime_checkable,
)
from dataclasses import dataclass, field
from abc import abstractmethod
from enum import Enum


ATTR_KWARG = "_attrs"


class HTMLRenderable(Protocol):
    def render(self, buffer: StringIO | None) -> str:
        ...


class ElementBuilderType(Enum):
    Normal = 0
    Void = 0


@runtime_checkable
class SupportsStr(Protocol):
    @abstractmethod
    def __str__(self) -> str:
        ...


class ElementBuilder(Protocol):
    def __call__(
        self,
        child: Renderable | None = None,
        _attrs: Mapping[str, SupportsStr | bool] | None = None,
        **attributes: SupportsStr | bool,
    ) -> Element:
        ...


class VoidElementBuilder(Protocol):
    def __call__(
        self,
        _attrs: Mapping[str, SupportsStr | bool] | None = None,
        **attributes: SupportsStr | bool,
    ) -> Element:
        ...


Renderable: TypeAlias = SupportsStr | HTMLRenderable | list["Renderable"]


@dataclass
class Element(HTMLRenderable):
    element_tag: str
    is_void: bool
    child: Renderable | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)

    def _render_attributes(self, buffer: StringIO):

        attribute_kwarg: dict = self.kwargs.get(ATTR_KWARG, {})

        if ATTR_KWARG in self.kwargs:
            del self.kwargs[ATTR_KWARG]

        for attr, value in self.kwargs.items():
            match attr:
                case "class_name":
                    buffer.write(f" class='{value}'")
                case _:
                    # Swap '_' with '-'
                    formatted_attr = attr.replace("_", "-")
                    delimeter = (
                        '"' if isinstance(value, str) and "'" in value else "'"
                    )

                    buffer.write(
                        f" {formatted_attr}={delimeter}{value}{delimeter}"
                    )

        for attr, value in attribute_kwarg.items():
            # TODO: Throw error on attribute with illegal characters
            delimeter = '"' if isinstance(value, str) and "'" in value else "'"
            buffer.write(f" {attr}={delimeter}{value}{delimeter}")
        buffer.write(">")

    def _render_child(self, child: Any, buffer: StringIO):
        match child:
            case list(children):
                siblings = Siblings(children)
                siblings.render(buffer)
            case Element():
                child.render(buffer)
            case int() | float() | str():
                buffer.write(str(child))
            case None:
                return
            case _:
                raise NotImplemented("Invalid node child type")

    def render(self, buffer: StringIO | None = None) -> str:
        el_start = f"<{self.element_tag}"
        if buffer is None:
            buffer = StringIO()
        buffer.write(el_start)

        self._render_attributes(buffer)

        if self.is_void:
            return buffer.getvalue()

        self._render_child(self.child, buffer)
        buffer.write(f"</{self.element_tag}>")
        return buffer.getvalue()


@dataclass
class Siblings(HTMLRenderable):
    elements: list[Renderable] = field(default_factory=list)

    def render(self, buffer: StringIO | None = None) -> str:
        if buffer is None:
            buffer = StringIO()

        for node in self.elements:
            match node:
                case list(children):
                    siblings = Siblings(children)
                    siblings.render(buffer)
                case Element():
                    node.render(buffer)
                case int() | float() | str():
                    buffer.write(str(node))
                case None:
                    continue
                case _:
                    raise NotImplemented("Invalid node child type")

        return buffer.getvalue()


_builders: dict[str, ElementBuilderType] = {}


def _dom_element(element_tag: str) -> ElementBuilder:
    def element_builder(
        child: Renderable | None = None, _attrs: Mapping | None = None, **kwargs
    ) -> Element:
        return Element(
            element_tag,
            False,
            child,
            {ATTR_KWARG: _attrs if _attrs is not None else {}, **kwargs},
        )

    _builders[element_tag] = ElementBuilderType.Normal
    return element_builder


def _void_dom_element(element_tag: str) -> VoidElementBuilder:
    def void_element_builder(
        _attrs: Mapping | None = None, **kwargs
    ) -> Element:
        return Element(
            element_tag,
            True,
            None,
            {ATTR_KWARG: _attrs if _attrs is not None else {}, **kwargs},
        )

    _builders[element_tag] = ElementBuilderType.Void
    return void_element_builder


def get_builder(element: str) -> ElementBuilderType | None:
    return _builders.get(element)


# Particle builders for void html elements
area = _void_dom_element("area")
base = _void_dom_element("base")
br = _void_dom_element("br")
col = _void_dom_element("col")
embed = _void_dom_element("embed")
hr = _void_dom_element("hr")
img = _void_dom_element("img")
Input = _void_dom_element("input")
link = _void_dom_element("link")
meta = _void_dom_element("meta")
source = _void_dom_element("source")
track = _void_dom_element("track")
wbr = _void_dom_element("wbr")


# Particle builders for normal html elements
div = _dom_element("div")
h1 = _dom_element("h1")
h2 = _dom_element("h2")
h3 = _dom_element("h3")
h4 = _dom_element("h4")
h5 = _dom_element("h5")
h6 = _dom_element("h6")
a = _dom_element("a")
abbr = _dom_element("abbr")
address = _dom_element("address")
article = _dom_element("article")
aside = _dom_element("aside")
audio = _dom_element("audio")
b = _dom_element("b")
bdi = _dom_element("bdi")
bdo = _dom_element("bdo")
blockquote = _dom_element("blockquote")
body = _dom_element("body")
button = _dom_element("button")
canvas = _dom_element("canvas")
caption = _dom_element("caption")
cite = _dom_element("cite")
code = _dom_element("code")
colgroup = _dom_element("colgroup")

content = _dom_element("content")
data = _dom_element("data")
datalist = _dom_element("datalist")
dd = _dom_element("dd")
Del = _dom_element("del")
details = _dom_element("details")
dfn = _dom_element("dfn")
dialog = _dom_element("dialog")
dl = _dom_element("dl")
dt = _dom_element("dt")
em = _dom_element("em")
fieldset = _dom_element("fieldset")
figcaption = _dom_element("figcaption")
figure = _dom_element("figure")
footer = _dom_element("footer")
form = _dom_element("form")
head = _dom_element("head")
header = _dom_element("header")
hgroup = _dom_element("hgroup")
html = _dom_element("html")
i = _dom_element("i")
iframe = _dom_element("iframe")
ins = _dom_element("ins")
kbd = _dom_element("kbd")
label = _dom_element("label")
legend = _dom_element("legend")
li = _dom_element("li")
main = _dom_element("main")
Map = _dom_element("map")
mark = _dom_element("mark")
menu = _dom_element("menu")
meter = _dom_element("meter")
nav = _dom_element("nav")
noscript = _dom_element("noscript")
Object = _dom_element("object")
ol = _dom_element("ol")
optgroup = _dom_element("optgroup")
option = _dom_element("option")
output = _dom_element("output")
p = _dom_element("p")
picture = _dom_element("picture")
pre = _dom_element("pre")
progress = _dom_element("progress")
q = _dom_element("q")
rp = _dom_element("rp")
rt = _dom_element("rt")
ruby = _dom_element("ruby")
s = _dom_element("s")
samp = _dom_element("samp")
script = _dom_element("script")
section = _dom_element("section")
select = _dom_element("select")
slot = _dom_element("slot")
small = _dom_element("small")
span = _dom_element("span")
strong = _dom_element("strong")
style = _dom_element("style")
sub = _dom_element("sub")
summary = _dom_element("summary")
sup = _dom_element("sup")
table = _dom_element("table")
tbody = _dom_element("tbody")
td = _dom_element("td")
template = _dom_element("template")
textarea = _dom_element("textarea")
tfoot = _dom_element("tfoot")
th = _dom_element("th")
thead = _dom_element("thead")
time = _dom_element("time")
title = _dom_element("title")
tr = _dom_element("tr")
u = _dom_element("u")
ul = _dom_element("ul")
Var = _dom_element("var")
video = _dom_element("video")

Document = lambda root: f"<!DOCTYPE html>{root.render()}"
