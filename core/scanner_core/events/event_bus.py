from typing import List, Tuple

from .event import Event
from .event_types import EventType


class EventBus:
    """
    Collects events during one engine cycle.
    Handles priority ordering and deduplication.
    """

    _PRIORITY_ORDER = [
        # Critical invalidations
        EventType.CONTEXT_INVALIDATED,
        EventType.ZONE_INVALIDATED,

        # Scenario lifecycle
        EventType.SCENARIO_CANCELLED,
        EventType.SCENARIO_COMPLETED,
        EventType.SCENARIO_CONFIRMED,

        # Progress & reaction
        EventType.TRACKING_PROGRESS,
        EventType.REACTION_DETECTED,
        EventType.ZONE_REACTED,
        EventType.ZONE_TOUCHED,

        # Structural
        EventType.CORRECTION_STARTED,
        EventType.IMPULSE_EXHAUSTED,
        EventType.IMPULSE_DETECTED,

        # Informational
        EventType.ZONE_CREATED,
        EventType.MARKET_CONTEXT_CHANGED,
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
