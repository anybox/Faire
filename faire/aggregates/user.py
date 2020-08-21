"""
⚠ Toy implementation: not to be used in prod ⚠
TodoList entities
"""
from dataclasses import dataclass, field
from typing import List, Dict
from uuid import uuid4

from faire.aggregates.aggregate import DefaultFactory, Aggregate
from faire.utils import PrettyDisplayMixin


class Task(PrettyDisplayMixin):
    name: str = None


class TodoList(Aggregate, PrettyDisplayMixin):
    name: str = None
    tasks: Dict[uuid4, Task] = DefaultFactory(lambda: {})


__all__ = ["Task", "TodoList"]
