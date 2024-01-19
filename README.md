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

There are basically two steps to using pyml: 
1 - Generate html in **.pyx** files using the **pysx** macro
2 - Import the .pyx and accessing the generated html

Example: 
```python
### views.pyx
"""
A .pyx files is just like a normal python source file, but with one caveat, they can
contain macro expressions. A macro expression is just like a normal function call, but
if the function name is followed by a '!', the expression is parsed as a macro call.
"""

from pyml.macros import pysx

title = pysx!( 
    h1 {
        "hello world"
    }
);


### app.py
import pysx.activate # 'pysx.activate' must appear before importing any .pyx module
from  .views import title

print(title)
```


### Pysx syntax

The syntax used with the pysx macro is html-like and was inspired by [rsx](https://dioxuslabs.com/learn/0.4/reference/rsx).



