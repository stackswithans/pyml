from io import StringIO
from typing import Callable, TypeVar, ParamSpec
from pyml.elements import *
import time as ptime


def pymain():

    start = ptime.time()

    res = div(
        class_name="hello_world",
        style="background-color: 'blue';",
        child=div(
            style="background-color: 'yellow';",
            child="Hello world",
        ),
    )

    end = ptime.time()

    print(f"Execution time: {end - start}")
    print(res)


pymain()
