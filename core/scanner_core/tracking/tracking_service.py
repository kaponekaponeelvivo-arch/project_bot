from typing import Dict

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine import ScenarioState


class TrackingService:
    """
    Tracks price movement AFTER SCENARIO_CONFIRMED.
    Emits TRACKING_PROGRESS every N%.
    """

    STEP_PERCENT = 3.0

    def __init__(self) -> None:
        self._confirm_price: Dict[str, float] = {}
        self._last_step: Dict[str, int] = {}

    # ===============================
    # LIFECYCLE
    # ===============================
    def start(self, symbol: str, price: float) -> None:
        self._confirm_price[symbol] = price
        self._last_step[symbol] = 0

    def stop(self, symbol: str) -> None:
        self._confirm_price.pop(symbol, None)
        self._last_step.pop(symbol, None)

    # ===============================
    # MAIN
    # ===============================
    def analyze(
        self,
        symbol: str,
        market_data: dict,
        scenario_state: ScenarioState,
        direction: str,
        event_bus: EventBus,
    ) -> None:

        if scenario_state != ScenarioState.CONFIRMED:
            return

        if symbol not in self._confirm_price:
            return

        candles = market_data.get("candles", [])
        if not candles:
            return

        confirm_price = self._confirm_price[symbol]
        last_close = candles[-1]["close"]

        if direction == "LONG":
            move_percent = (last_close - confirm_price) / confirm_price * 100
        else:
            move_percent = (confirm_price - last_close) / confirm_price * 100

        if move_percent <= 0:
            return

        step = int(move_percent // self.STEP_PERCENT)

        if step <= self._last_step.get(symbol, 0):
            return

        self._last_step[symbol] = step

        event_bus.publish(
            Event(
                type=EventType.TRACKING_PROGRESS,
                symbol=symbol,
                payload={
                    "move_percent": round(move_percent, 2),
                    "step": step,
                },
            )
        )
