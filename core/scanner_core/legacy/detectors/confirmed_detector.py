from typing import List

from core.scanner_core.events import Event, EventType
from core.scanner_core.events.event_bus import EventBus


class ConfirmedDetector:
    """
    Confirms scenario after valid reaction.
    """

    def analyze(
        self,
        symbol: str,
        market_data: dict,
        direction: str,
        market_context: str,
        event_bus: EventBus,
    ) -> None:

        candles: List[dict] = market_data.get("candles", [])
        if len(candles) < 3:
            return

        last = candles[-1]
        prev = candles[-2]

        # ===============================
        # 1️⃣ Local structure break
        # ===============================
        structure_break = False

        if direction == "LONG":
            structure_break = last["close"] > prev["high"]
        elif direction == "SHORT":
            structure_break = last["close"] < prev["low"]

        # ===============================
        # 2️⃣ Impulse candle
        # ===============================
        body = abs(last["close"] - last["open"])
        full = last["high"] - last["low"]

        impulse_candle = (
            full > 0 and body / full >= 0.6
        )

        direction_ok = (
            direction == "LONG" and last["close"] > last["open"]
        ) or (
            direction == "SHORT" and last["close"] < last["open"]
        )

        # ===============================
        # 3️⃣ FINAL DECISION
        # ===============================
        if direction_ok and (structure_break or impulse_candle):
            event_bus.publish(
                Event(
                    type=EventType.SCENARIO_CONFIRMED,
                    symbol=symbol,
                )
            )
