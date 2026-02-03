from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine import ScenarioState


class CompletedDetector:
    """
    Finalizes scenario lifecycle.
    Decides COMPLETED or CANCELLED.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        scenario_state: ScenarioState,
        event_bus: EventBus,
    ) -> None:
        """
        Rules:
        - COMPLETED: scenario was CONFIRMED and market continues in direction
        - CANCELLED: structure broken or context invalidated
        """

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 2:
            return

        last = candles[-1]
        prev = candles[-2]

        # ===============================
        # CANCEL CONDITIONS
        # ===============================
        if scenario_state in (
            ScenarioState.CORRECTION,
            ScenarioState.REACTION,
        ):
            # sharp opposite candle = invalidation
            body = abs(last["close"] - last["open"])
            full = last["high"] - last["low"]

            if full > 0 and body / full > 0.7:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_CANCELLED,
                        symbol=symbol,
                    )
                )
                return

        # ===============================
        # COMPLETE CONDITIONS
        # ===============================
        if scenario_state == ScenarioState.CONFIRMED:
            continuation = (
                last["close"] > prev["close"]
                or last["close"] < prev["close"]
            )

            if continuation:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_COMPLETED,
                        symbol=symbol,
                    )
                )
