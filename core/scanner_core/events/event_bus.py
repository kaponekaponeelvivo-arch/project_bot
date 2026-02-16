from typing import List, Tuple

from .event import Event
from .event_types import EventType


class EventBus:

    _PRIORITY_ORDER = [

        # Context
        EventType.CONTEXT_INVALIDATED,
        EventType.MARKET_CONTEXT_CHANGED,

        # Scenario lifecycle
        EventType.SCENARIO_CANCELLED,
        EventType.SCENARIO_CONFIRMED,

        # Reaction
        EventType.ZONE_REACTED,

        # Correction / Impulse
        EventType.CORRECTION_STARTED,
        EventType.IMPULSE_DETECTED,

        # Watchlist
        EventType.WATCHLIST_UPDATED,
    ]

    def __init__(self) -> None:
        self._events: List[Event] = []
        self._dedup: set[Tuple[str, EventType]] = set()

    def publish(self, event: Event) -> None:
        key = (event.symbol, event.type)
        if key in self._dedup:
            return

        self._dedup.add(key)
        self._events.append(event)

    def has_events(self) -> bool:
        return bool(self._events)

    def drain(self) -> List[Event]:
        ordered = sorted(
            self._events,
            key=lambda e: self._priority_index(e.type),
            reverse=True,
        )

        self._events.clear()
        self._dedup.clear()
        return ordered

    def _priority_index(self, event_type: EventType) -> int:
        try:
            return self._PRIORITY_ORDER.index(event_type)
        except ValueError:
            return -1
