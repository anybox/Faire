"""
⚠ Toy implementation: not to be used in prod ⚠
Events related to TodoLists
"""
from dataclasses import dataclass

from faire.events.event import Event


@dataclass(frozen=True)
class TodoListCreated(Event):
    name: str


@dataclass(frozen=True)
class TaskAddedToList(Event):
    id: str
    name: str


__all__ = ["TodoListCreated", "TaskAddedToList"]
