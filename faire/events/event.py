"""
⚠ Toy implementation: not to be used in prod ⚠
base class for events
"""
from dataclasses import dataclass

from faire.utils import PrettyDisplayMixin


@dataclass(frozen=True, repr=False)
class Event(PrettyDisplayMixin):
    """
    Base event class
    """

    stream_id: str
