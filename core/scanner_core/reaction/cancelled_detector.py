from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine import ScenarioState


class CancelledDetector:
    """
    Detects scenario invalidation.
    """

    MAX_ADVERSE_MOVE = 2.0  # % против сценария после CONFIRMED

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
            adverse = (confirm_price - last_close) / confirm_price * 100
        else:
            adverse = (last_close - confirm_price) / confirm_price * 100

        if adverse >= self.MAX_ADVERSE_MOVE:
            event_bus.publish(
                Event(
                    type=EventType.SCENARIO_CANCELLED,
                    symbol=symbol,
                    payload={
                        "adverse_move": round(adverse, 2),
                    },
                )
            )
