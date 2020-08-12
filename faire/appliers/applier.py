"""
⚠ Toy implementation: not to be used in prod ⚠
"""
from typing import Callable

from faire.events.event import Event


class Applier:
    __appliers = {}

    @classmethod
    def register(cls, applier: Callable) -> Callable:
        """
        Decorator used to register appliers
        assumptions:
        * function prototype should look like `def bla(event:EventType, entity:EntityType) -> EntityType`
        * (For now) only one applier should be implemented per type of event
        :param applier:
        :return:
        """

        event_type = list(applier.__annotations__.values())[0]
        cls.__appliers[event_type] = applier

        return applier

    @classmethod
    def get_applier(cls, event: Event):
        def not_found_applier(event: Event, entity=None):
            raise ValueError(
                f"No applier found for event {event.__class__.__name__}"
            )

        return cls.__appliers.get(event.__class__, not_found_applier)


__all__ = ["Applier"]
