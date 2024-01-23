# Pyml

Pyml is a python library that allows users to non-static HTML through the use of a custom implementation of syntatic macros for python.
By leveraging the power of syntatic macros, pyml offers the familiarity and full feature richness of python, with minimal syntatical overhead.

Pyml is in a very early stage of developmenet. Any feedback, contribuitions or bug reports will be greatly appreciated.

## Installation

Pyml can be installed using pip:

```bash
pip install pyml
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

from pyml.macros import pysx

title = pysx!( 
    h1 {
        "hello world"
    }
)


### app.py
import pysx.activate # 'pysx.activate' must appear before importing any .pyxp module
from  .views import title

print(title)
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
### Components

Components are just decorated functions that return pysx: 
```python
### views.pyxp
from pyml.macros import pysx
from pyml.component import component, Props

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
                py { props.children } 
            }, 
        }
    )

def index(): 
    return pysx!(
        Scaffold {
            h1 {
                "hello world"
            }
        }
    )

```
