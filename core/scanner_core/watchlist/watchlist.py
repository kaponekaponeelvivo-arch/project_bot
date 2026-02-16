from typing import Dict, List
from collections import defaultdict

from core.scanner_core.state_machine import ScenarioState
from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus

from .priority import STATE_TO_PRIORITY, WatchPriority


class Watchlist:

    def __init__(self) -> None:
        self._items: Dict[str, ScenarioState] = {}
        self._last_snapshot = None  # 🔥 новое

    # ===============================
    def update(self, symbol: str, state: ScenarioState) -> None:
        if state in (ScenarioState.COMPLETED, ScenarioState.CANCELLED):
            self._items.pop(symbol, None)
            return

        self._items[symbol] = state

    def remove(self, symbol: str) -> None:
        self._items.pop(symbol, None)

    # ===============================
    def snapshot(self) -> Dict[WatchPriority, List[str]]:
        buckets: Dict[WatchPriority, List[str]] = defaultdict(list)

        for symbol, state in self._items.items():
            priority = STATE_TO_PRIORITY.get(state)
            if not priority:
                continue

            buckets[priority].append(symbol)

        for symbols in buckets.values():
            symbols.sort()

        return dict(sorted(buckets.items(), key=lambda x: x[0].value))

    # ===============================
    def emit(self, event_bus: EventBus) -> None:
        snapshot = self.snapshot()

        # 🔥 Публикуем только если изменилось
        if snapshot == self._last_snapshot:
            return

        self._last_snapshot = snapshot

        event_bus.publish(
            Event(
                type=EventType.WATCHLIST_UPDATED,
                symbol="WATCHLIST",
                payload={"snapshot": snapshot},
            )
        )
