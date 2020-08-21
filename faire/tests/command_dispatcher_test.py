from dataclasses import dataclass

from faire.events.event import Event
from faire.eventstore import EventStore


@dataclass(frozen=True)
class DummyEvent(Event):
    pass


def test_EventStore():
    store = EventStore("test_store")

    store.add_event(DummyEvent(stream_id="stream1"))
    store.add_event(DummyEvent(stream_id="stream1"))
    store.add_event(DummyEvent(stream_id="stream2"))
    store.add_event(DummyEvent(stream_id="stream1"))
    store.add_event(DummyEvent(stream_id="stream3"))
    store.add_event(DummyEvent(stream_id="stream2"))

    assert len(store.get_stream("stream1")) == 3
    assert len(store.get_stream("stream2")) == 2
    assert len(store.get_stream("stream3")) == 1
