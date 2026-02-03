from typing import List, Tuple

from .event import Event
from .event_types import EventType


class EventBus:
    """
    Collects events during one engine cycle.
    Handles priority ordering and deduplication.
    """

    # Higher index = higher priority
    _PRIORITY_ORDER = [
        # Context / structure (highest priority)
        EventType.CONTEXT_INVALIDATED,
        EventType.MARKET_CONTEXT_CHANGED,
        EventType.STRUCTURE_BROKEN,

        # Scenario lifecycle
        EventType.SCENARIO_CANCELLED,
        EventType.SCENARIO_COMPLETED,
        EventType.SCENARIO_CONFIRMED,
        EventType.SCENARIO_STARTED,

        # Zones & reaction
        EventType.ZONE_INVALIDATED,
        EventType.ZONE_REACTED,

        # Impulse / correction
        EventType.CORRECTION_STARTED,
        EventType.IMPULSE_EXHAUSTED,
        EventType.IMPULSE_DETECTED,
    ]

    def __init__(self) -> None:
        self._events: List[Event] = []
        self._dedup: set[Tuple[str, EventType]] = set()

    def publish(self, event: Event) -> None:
        """
        Add event to bus with deduplication by (symbol, event_type).
        """
        key = (event.symbol, event.type)
        if key in self._dedup:
            return

        self._dedup.add(key)
        self._events.append(event)

    def has_events(self) -> bool:
        return bool(self._events)

    def drain(self) -> List[Event]:
        """
        Return events sorted by priority and clear bus.
        """
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
