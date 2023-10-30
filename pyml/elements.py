from io import StringIO
from typing import Callable, TypeVar, ParamSpec
import time as ptime


def _dom_element(element_tag: str, void=False) -> Callable[..., str]:
    def element(child: object = None, **kwargs) -> str:
        child = "" if child is None else str(child)

        attrs = StringIO()
        for i, (attr, value) in enumerate(kwargs.items()):
            match attr:
                case "class_name":
                    attrs.write(f"class='{value}'")
                case _:
                    # Swap '_' with '-'
                    formatted_attr = attr.replace("_", "-")
                    delimeter = (
                        '"' if isinstance(value, str) and "'" in value else "'"
                    )

                    attrs.write(
                        f"{formatted_attr}={delimeter}{value}{delimeter}"
                    )

            if i != len(kwargs.items()) - 1:
                attrs.write(" ")
        if not void:
            return f"<{element_tag} {attrs.getvalue()}>{child}</{element_tag}>"
        else:
            return f"<{element_tag} {attrs.getvalue()}>"

    return element


# Particle builders for void html elements
area = _dom_element("area", void=True)
base = _dom_element("base", void=True)
br = _dom_element("br", void=True)
col = _dom_element("col", void=True)
embed = _dom_element("embed", void=True)
hr = _dom_element("hr", void=True)
img = _dom_element("img", void=True)
Input = _dom_element("input", void=True)
link = _dom_element("link", void=True)
meta = _dom_element("meta", void=True)
source = _dom_element("source", void=True)
track = _dom_element("track", void=True)
wbr = _dom_element("wbr", void=True)

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
