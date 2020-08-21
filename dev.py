import functools
from inspect import ismethod, isfunction


class Mum:
    def __init_subclass__(cls, **kwargs):
        print(kwargs)


class Child(Mum, caca=123):
    pass
