from io import StringIO
from typing import Callable, TypeVar, ParamSpec
from pyml.elements import *
import time as ptime


def pymain():

    start = ptime.time()
    html_res = div(
        child=[div(child=[div() for i in range(100)]) for i in range(1000)]
    )
    end = ptime.time()
    # print(html_res)
    print("Pyml time: ", end - start)

    start = ptime.time()
    with open("quick_test.html", "r", encoding="utf8") as f:
        html_res = f.read()
    end = ptime.time()
    # print(html_res)
    print("Opening file time: ", end - start)


pymain()
