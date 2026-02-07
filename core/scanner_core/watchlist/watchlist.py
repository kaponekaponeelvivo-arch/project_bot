from typing import Dict

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine import ScenarioState
from .priority import WatchPriority


class Watchlist:
    """
    Stores symbols under observation and emits aggregated updates.
    """

    def __init__(self) -> None:
        self._items: Dict[str, ScenarioState] = {}

    # ===============================
    # CORE API
    # ===============================
    def process(self, symbol: str, market_data: dict) -> None:
        """
        Public entry point (used by tests).
        """
        if symbol not in self._items:
            self._items[symbol] = ScenarioState.TREND_ACTIVE

    def update(self, symbol: str, state: ScenarioState) -> None:
        self._items[symbol] = state

    def remove(self, symbol: str) -> None:
        self._items.pop(symbol, None)

    # ===============================
    # EVENTS
    # ===============================
    def emit(self, event_bus: EventBus) -> None:
        """
        Emit single aggregated WATCHLIST_UPDATED event.
        """
        event_bus.publish(
            Event(
                type=EventType.WATCHLIST_UPDATED,
                symbol="WATCHLIST",
                payload={
                    "items": self.snapshot(),
                },
            )
        )

    # ===============================
    # UX
    # ===============================
    def snapshot(self) -> Dict[str, str]:
        """
        Sorted snapshot for notifications / tests.
        """
        return {
            symbol: state.value
            for symbol, state in sorted(self._items.items())
        }

    def summary(self) -> str:
        """
        Human-readable summary (used in manual tests).
        """
        if not self._items:
            return "📊 WATCHLIST: пусто"

        lines = ["📊 WATCHLIST:"]
        for symbol, state in sorted(self._items.items()):
            lines.append(f"👀 {symbol}: {state.value}")

        return "\n".join(lines)
