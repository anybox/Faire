"""
The event store.
"""
from typing import List

from faire.events.event import Event


class EventStore:
    """
    This is a dummy, dead simple implementation
    """

    def add_event(self, event: Event) -> None:
        """
        Stores an event
        """

    def get_stream(self, stream_id: str) -> List[Event]:
        """
        :return: Events that belong to the stream with given `stream_id`
        """
