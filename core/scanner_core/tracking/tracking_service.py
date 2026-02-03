from typing import Optional

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine import ScenarioState


class TrackingService:
    """
    Tracks scenario progress AFTER CONFIRMED.
    Not a signal. Informational only.
    """

    def __init__(self, step_percent: float = 3.0) -> None:
        self._base_price: Optional[float] = None
        self._last_notified_step: int = 0
        self._step_percent = step_percent

    def reset(self) -> None:
        self._base_price = None
        self._last_notified_step = 0

    def on_confirmed(self, price: float) -> None:
        """
        Initialize tracking from CONFIRMED price.
        """
        self._base_price = price
        self._last_notified_step = 0

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        scenario_state: ScenarioState,
        event_bus: EventBus,
    ) -> None:

        if scenario_state != ScenarioState.CONFIRMED:
            return

        if self._base_price is None:
            return

        candles = market_data.get("candles", [])
        if not candles:
            return

        last_price = candles[-1]["close"]

        if direction == "LONG":
            move_percent = (last_price - self._base_price) / self._base_price * 100
        else:
            move_percent = (self._base_price - last_price) / self._base_price * 100

        if move_percent <= 0:
            return

        step = int(move_percent // self._step_percent)

        if step <= self._last_notified_step:
            return

        self._last_notified_step = step

        event_bus.publish(
            Event(
                type=EventType.SCENARIO_PROGRESS,
                symbol=symbol,
                payload={
                    "progress_percent": round(step * self._step_percent, 2),
                },
            )
        )
