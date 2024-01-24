# Pyml

Pyml is a python library that allows developers to generate non-static HTML through the use of a custom implementation of syntactic macros for python.
By leveraging the power of syntatic macros, pyml offers the familiarity and full feature richness of python, with minimal syntactical overhead.

Pyml is framework agnostic and can be used with any web framework/server that supports
the returning HTML strings as a response.

Pyml is in a very early stage of developmenet. Any feedback, contribuitions or bug reports will be greatly appreciated.

## Installation

Pyml can be installed using pip:

```bash
pip install pyml3
```` 

## Using pyml

Pyml relies on the concept of [syntactic macros](https://en.wikipedia.org/wiki/Macro_(computer_science)) to allow embedding of markup within 
python code. At the time of writing, python does not offer builtin support for syntactic macros (although that might change in the [future](https://peps.python.org/pep-0638/)).
The library implements macros by relying on a custom implementation that uses [import hooks](https://docs.python.org/3/reference/import.html) and
a custom file extension.

There are two steps to using pyml: 
1. Generate html in **.pyxp** files using the **pysx** macro
2. Import the .pyxp file and access the pysx output

Example: 
```python
### views.pyxp
"""
A .pyxp files is just like a normal python source file, but with one caveat, they can
contain macro expressions. A macro expression is just like a normal function call, but
if the function name is followed by a '!', the expression is parsed as a macro call.
"""

from pyml import pysx

title = pysx!( 
    h1 {
        "hello world"
    }
)


### app.py
import pyml.activate # 'pysx.activate' must appear before importing any .pyxp module
from  .views import title

print(title) # <h1>hello world</h1>
```


### Elements

The syntax used with the pysx macro is html-like and was inspired by [rsx](https://dioxuslabs.com/learn/0.4/reference/rsx).
In pysx, elements are referenced by the name of the element, followed by their attributes and children in between curly braces: 
```python
h1 = pysx!(h1 {
    style: "color:blue", 
    "Hello world"
}) # expands to: <h1 style="color: blue">Hello world</h1>
    
```
Void elements like `input` are checked during expansion to make ensure that they don't have children: 
```python
h1 = pysx!(input { "bad child"}) # Error: Void element 'input' cannot have children
```

### Expressions
Pysx has the following types of expressions: 
- Numbers: `1, 2, 1.5, 8`
- Strings: `"Foo", 'Bar'`
- Identifiers (Variable reference):`py_var, some_var` 

Expressions can be used as attribute values and as the children of elements. `Identifiers` are resolved using python's name resolution
rules: 
```python
hello_word = "Hello world in a variable"

print(
    pysx!(div {
        hello_word
    })
) # expands to: <div>Hello world in variable</div>
```

The `py`element allows the use of any arbitary python expression 
within a pysx block: 
```python
pysx!(
    h1{
        "Even numbers from 1-100: ", 
        div {
            py { ", ".join([str(i) for i in range(1, 101) if i % 2 == 0]) }
        }
    }
)
```
### Conditional rendering

You can use if statements within rsx to render content conditionally:
```python
### if_stmt.pyxp
from pyml import pysx

is_visible = False

page = pysx!(
    div {
        if is_visible {
            "hello world" 
        },
    }
) 
print(page) # <div></div>


# You can also use elif and else statements
lit_type = "string"
page = pysx!(
    div {
        if lit_type == "list_lit" {
            "[]"
        }
        elif lit_type == "float" {
            "3.14"
        }
        elif lit_type == "string" {
            "Hello world"
        } else {
            "unknown type"
        }
    }
) 
print(page) # <div>Hello world</div>
```

### Loops

You can also use for loops within pysx: 
```python
### for_stmt.pyxp
from pyml import pysx

word_list = ["hello world", "bye world"]
pysx!(
    div {
        h1 {
            "List content" 
        }, 
        for i, word in enumerate(word_list) {
            b {
                i
            }, 
            b {
                word
            }
        } 
    }
)

```

### Components

Components are just functions decorated with the 
`pyml.component.component` decorator that return pysx.  
Components are invoked with the `props` arg, which is an object that contains
all the props that the component was initialized with. The `children` prop 
is a special prop that can be used to render the child elements  
passed to the component: 
```python
### views.pyxp
from pyml import pysx, component, Props

@component
def Scaffold(props: Props):
    return pysx!(
        "<!DOCTYPE html>", 
        html {
            head {
                meta {
                    charset: "utf-8"
                }, 
                meta {
                    name: "viewport", 
                    content: "width=device-width", 
                    initial-scale: 1
                } 
            }, 
            body{  
                style: py { f"background-color: {props.bg_color}" }
                py { props.children }
            }, 
        }
    )

def index(): 
    return pysx!(
        Scaffold {
            bg_color: "red",
            h1 {
                "hello world"
            }
        }
    )

```
Trying to access an unknown prop will result in a runtime error: 
```python
### views.pyxp
from pyml import pysx, component, Props

@component
def Scaffold(props: Props):
    return pysx!(
        h1 {
            py { props.message }
        }
    )

def index(): 
    return pysx!(
        Scaffold {  
        } # raises AttributeError: 'Props' object has no attribute 'message'. 
    )

print(index())
```
The above example fails because the `Scaffold` component attempts to get the `message` prop 
even though it wasn't invoked with it.

### Debugging pysx

If you would like to see the expanded version of a .pyxp for debugging or other purposes, without needing to import in another file, 
you can use the `expan.main` script: 
```bash
python -m expan.main path/to/pyxp/file.pyxp
```
The above command prints the expanded source to stdout. If you would like send the output to another file, just
use the `-o` option: 
```bash
python -m expan.main path/to/pyxp/file.pyxp -o path/to/output/file.py
```

## Example(s)

To see examples of pyml in use, check out the tiny app(s) in the [examples](examples/) folder.
