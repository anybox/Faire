from typing import Callable, NewType, Any
from uuid import uuid4

DefaultFactory = NewType("DefaultFactory", Callable[[], Any])


class Aggregate:
    """Base class for Aggregate with magic"""

    id: uuid4 = DefaultFactory(lambda: uuid4())

    def __init__(self, **kwargs):
        for attr_name, attr_type in self.__annotations__.items():
            if attr_name in kwargs:
                setattr(self, attr_name, kwargs[attr_name])
                continue
            if isinstance(attr_type, DefaultFactory):
                setattr(self, attr_name, attr_type())
            if attr_type in (str, int, float):
                setattr(self, attr_name, getattr(self.__class__, attr_name))
