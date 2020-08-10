"""
⚠ Toy implementation: not to be used in prod ⚠
TodoList entities
"""
from dataclasses import dataclass, field
from typing import List

from faire.utils import PrettyDisplayMixin


@dataclass(repr=False)
class Task(PrettyDisplayMixin):
    id: str
    name: str = None


@dataclass(repr=False)
class TodoList(PrettyDisplayMixin):
    id: str
    name: str = None
    tasks: List[Task] = field(default_factory=list)


__all__ = ["Task", "TodoList"]
