from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine.states import ScenarioState


class ReactionDetector:
    """
    Detects reaction on 15M timeframe.
    """

    def analyze(
        self,
        symbol: str,
        reaction_data: dict,   # 15M
        scenario,
        event_bus: EventBus,
    ) -> None:

        if scenario.state != ScenarioState.CORRECTION:
            return

        candles: List[dict] = reaction_data.get("candles", [])
        if len(candles) < 1:
            return

        last = candles[-1]

        correction_event = next(
            (e for e in reversed(scenario.events)
             if e.type == EventType.CORRECTION_STARTED),
            None,
        )

        if not correction_event:
            return

        zone_from = correction_event.payload.get("zone_from")
        zone_to = correction_event.payload.get("zone_to")
        direction = correction_event.payload.get("direction")

        if zone_from is None or zone_to is None:
            return

        # Touch zone
        touched = (
            last["low"] <= zone_to and
            last["high"] >= zone_from
        )

        if not touched:
            return

        # Impulse candle confirmation
        body = abs(last["close"] - last["open"])
        full = last["high"] - last["low"]

        if full == 0:
            return

        body_ratio = body / full

        bullish = last["close"] > last["open"]
        bearish = last["close"] < last["open"]

        direction_ok = (
            direction == "LONG" and bullish
        ) or (
            direction == "SHORT" and bearish
        )

        if direction_ok and body_ratio >= 0.6:

            payload = correction_event.payload.copy()
            payload["reaction_price"] = last["close"]

            event_bus.publish(
                Event(
                    type=EventType.SCENARIO_CONFIRMED,
                    symbol=symbol,
                    payload=payload,
                )
            )
