from typing import Dict, List
from collections import defaultdict

from core.scanner_core.state_machine import ScenarioState
from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus

from .priority import STATE_TO_PRIORITY, WatchPriority


class Watchlist:
    """
    Aggregated watchlist with priorities.
    Emits ONE event with full snapshot.
    """

    def __init__(self) -> None:
        self._items: Dict[str, ScenarioState] = {}

    # ===============================
    # CORE API (used by Engine)
    # ===============================
    def update(self, symbol: str, state: ScenarioState) -> None:
        if state in (ScenarioState.COMPLETED, ScenarioState.CANCELLED):
            self._items.pop(symbol, None)
            return

        self._items[symbol] = state

    def remove(self, symbol: str) -> None:
        self._items.pop(symbol, None)

    # ===============================
    # TEST / DEV COMPATIBILITY
    # ===============================
    def process(self, symbol: str, market_data: dict) -> None:
        """
        Compatibility layer for manual tests.
        """
        self.update(symbol, ScenarioState.TREND_ACTIVE)

    # ===============================
    # SNAPSHOT
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
    # UX HELPERS (tests / console)
    # ===============================
    def summary(self) -> str:
        snapshot = self.snapshot()
        if not snapshot:
            return "📊 WATCHLIST:\n(пусто)"

        lines = ["📊 WATCHLIST:"]
        for priority, symbols in snapshot.items():
            lines.append(f"{priority.name}:")
            for s in symbols:
                lines.append(f"  • {s}")

        return "\n".join(lines)

    # ===============================
    # EMIT
    # ===============================
    def emit(self, event_bus: EventBus) -> None:
        snapshot = self.snapshot()
        if not snapshot:
            return

        event_bus.publish(
            Event(
                type=EventType.WATCHLIST_UPDATED,
                symbol="WATCHLIST",
                payload={"snapshot": snapshot},
            )
        )
