from dataclasses import dataclass
from typing import Callable


class Props:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def component(component: Callable) -> Callable:
    def wrapper(**kwargs):
        return component(Props(**kwargs))

    return wrapper
