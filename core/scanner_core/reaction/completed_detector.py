from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine.states import ScenarioState


class CompletedDetector:
    """
    Detects scenario completion or cancellation
    based on TP2 or Stop level.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,          # 5M
        scenario,
        event_bus: EventBus,
    ) -> None:

        if scenario.state != ScenarioState.CONFIRMED:
            return

        candles: List[dict] = market_data.get("candles", [])
        if not candles:
            return

        last = candles[-1]

        confirmed_event = next(
            (e for e in reversed(scenario.events)
             if e.type == EventType.SCENARIO_CONFIRMED),
            None,
        )

        if not confirmed_event:
            return

        payload = confirmed_event.payload

        entry = payload.get("entry_price")
        stop = payload.get("stop_price")
        tp2 = payload.get("tp2_price")
        direction = payload.get("direction")

        if None in (entry, stop, tp2, direction):
            return

        # ===============================
        # LONG
        # ===============================
        if direction == "LONG":

            # Stop hit
            if last["low"] <= stop:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_CANCELLED,
                        symbol=symbol,
                        payload=payload,
                    )
                )
                return

            # TP2 reached
            if last["high"] >= tp2:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_COMPLETED,
                        symbol=symbol,
                        payload=payload,
                    )
                )
                return

        # ===============================
        # SHORT
        # ===============================
        if direction == "SHORT":

            # Stop hit
            if last["high"] >= stop:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_CANCELLED,
                        symbol=symbol,
                        payload=payload,
                    )
                )
                return

            # TP2 reached
            if last["low"] <= tp2:
                event_bus.publish(
                    Event(
                        type=EventType.SCENARIO_COMPLETED,
                        symbol=symbol,
                        payload=payload,
                    )
                )
                return
