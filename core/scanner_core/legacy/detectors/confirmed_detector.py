from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus
from core.scanner_core.state_machine.states import ScenarioState


class ConfirmedDetector:
    """
    Calculates entry, stop and TP levels.
    """

    STOP_BUFFER_PERCENT = 1.0

    def analyze(
        self,
        symbol: str,
        market_data: dict,      # 5M
        scenario,
        event_bus: EventBus,
    ) -> None:

        if scenario.state != ScenarioState.REACTION:
            return

        candles: List[dict] = market_data.get("candles", [])
        if not candles:
            return

        last = candles[-1]

        reaction_event = next(
            (e for e in reversed(scenario.events)
             if e.type == EventType.ZONE_REACTED),
            None,
        )

        if not reaction_event:
            return

        payload = reaction_event.payload.copy()

        direction = payload.get("direction")
        impulse_high = payload.get("impulse_high")
        impulse_low = payload.get("impulse_low")

        if None in (direction, impulse_high, impulse_low):
            return

        # ===============================
        # ENTRY
        # ===============================
        entry_price = last["close"]

        # ===============================
        # STOP (correction extreme ±1%)
        # ===============================
        correction_low = min(
            c["low"] for c in payload.get("candles_1h", [])
        )
        correction_high = max(
            c["high"] for c in payload.get("candles_1h", [])
        )

        if direction == "LONG":
            stop_price = correction_low * (1 - self.STOP_BUFFER_PERCENT / 100)
        else:
            stop_price = correction_high * (1 + self.STOP_BUFFER_PERCENT / 100)

        risk = abs(entry_price - stop_price)

        if risk <= 0:
            return

        # ===============================
        # TP LEVELS
        # ===============================
        if direction == "LONG":
            tp1 = entry_price + risk * 1
            tp2 = entry_price + risk * 2
            tp3 = impulse_high
        else:
            tp1 = entry_price - risk * 1
            tp2 = entry_price - risk * 2
            tp3 = impulse_low

        payload.update({
            "entry_price": round(entry_price, 6),
            "stop_price": round(stop_price, 6),
            "tp1_price": round(tp1, 6),
            "tp2_price": round(tp2, 6),
            "tp3_price": round(tp3, 6),
        })

        event_bus.publish(
            Event(
                type=EventType.SCENARIO_CONFIRMED,
                symbol=symbol,
                payload=payload,
            )
        )
