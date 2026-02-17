from typing import List, Tuple, Set
from core.scanner_core.events.event import Event
from core.scanner_core.events.event_types import EventType


class EventBus:

    def __init__(self) -> None:
        self._events: List[Event] = []
        self._dedup: Set[Tuple[str, EventType]] = set()
        self._history: Set[Tuple[str, EventType]] = set()

    def publish(self, event: Event) -> None:
        key = (event.symbol, event.type)

        # защита в рамках одного тика
        if key in self._dedup:
            return

        # защита в рамках активного сценария
        if key in self._history:
            return

        self._dedup.add(key)
        self._history.add(key)
        self._events.append(event)

    def has_events(self) -> bool:
        """
        Проверка наличия событий в очереди.
        Нужен для послойного применения FSM.
        """
        return bool(self._events)

    def drain(self) -> List[Event]:
        events = list(self._events)
        self._events.clear()
        self._dedup.clear()
        return events

    def clear_history(self, symbol: str) -> None:
        self._history = {k for k in self._history if k[0] != symbol}
