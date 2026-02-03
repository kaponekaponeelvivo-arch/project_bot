from typing import Dict, Optional

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine import ScenarioState


class TrackingService:
    """
    Tracks scenario progress AFTER CONFIRMED.
    Emits progress events every N%.
    """

    def __init__(self, step_percent: float = 3.0) -> None:
        self._step = step_percent
        self._start_price: Dict[str, float] = {}
        self._last_notified_step: Dict[str, int] = {}

    def start(
        self,
        symbol: str,
        confirmed_price: float,
    ) -> None:
        """
        Initialize tracking from CONFIRMED price.
        """
        self._start_price[symbol] = confirmed_price
        self._last_notified_step[symbol] = 0

    def stop(self, symbol: str) -> None:
        """
        Stop tracking scenario.
        """
        self._start_price.pop(symbol, None)
        self._last_notified_step.pop(symbol, None)

    def analyze(
        self,
        symbol: str,
        scenario_state: ScenarioState,
        market_data: dict,
        event_bus: EventBus,
    ) -> None:
        """
        Track price progress and emit events.
        """

        if scenario_state != ScenarioState.CONFIRMED:
            return

        if symbol not in self._start_price:
            return

        candles = market_data.get("candles", [])
        if not candles:
            return

        price = candles[-1]["close"]
        start_price = self._start_price[symbol]

        if start_price <= 0:
            return

        percent_move = ((price - start_price) / start_price) * 100
        step_index = int(percent_move // self._step)

        last_step = self._last_notified_step.get(symbol, 0)

        if step_index > last_step:
            self._last_notified_step[symbol] = step_index

            event_bus.publish(
                Event(
                    type=EventType.TRACKING_PROGRESS,
                    symbol=symbol,
                    payload={
                        "from_price": start_price,
                        "current_price": price,
                        "percent": round(percent_move, 2),
                        "step": step_index,
                    },
                )
            )
