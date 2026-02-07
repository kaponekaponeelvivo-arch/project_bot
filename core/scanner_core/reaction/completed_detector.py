from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine import ScenarioState


class CompletedDetector:
    """
    Detects successful scenario completion.
    Completion is based ONLY on movement from CONFIRMED price.
    """

    MIN_MOVE_PERCENT = 3.0  # configurable threshold

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        scenario_state: ScenarioState,
        confirm_price: float,
        direction: str,
        event_bus: EventBus,
    ) -> None:

        if scenario_state != ScenarioState.CONFIRMED:
            return

        candles: List[dict] = market_data.get("candles", [])
        if not candles:
            return

        last_close = candles[-1]["close"]

        if direction == "LONG":
            move = (last_close - confirm_price) / confirm_price * 100
        else:
            move = (confirm_price - last_close) / confirm_price * 100

        if move < self.MIN_MOVE_PERCENT:
            return

        event_bus.publish(
            Event(
                type=EventType.SCENARIO_COMPLETED,
                symbol=symbol,
                payload={
                    "move_percent": round(move, 2),
                },
            )
        )
